"""
API 路由 - 表单提交、数据查询
"""
import json
import sqlite3
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, UploadFile, File, Form, HTTPException, Depends, Request
from fastapi.responses import FileResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from config import DB_PATH, UPLOAD_DIR, MAX_FILE_SIZE, MAX_FILES_PER_SUBMISSION, ALLOWED_INDUSTRIES
from database import get_connection
from auth import verify_admin
from utils import sanitize_filename, sanitize_dirname
from services.ai_service import parse_file_with_ai
from services.feishu import sync_to_feishu
from services.miaodong import push_to_miaodong

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api")


def process_submission(submission_id: int, company: str, industry: str,
                       scenario: str, extra: str, saved_files: list):
    """后台任务：AI解析 + 飞书同步 + 秒懂推送"""
    print(f"  🔄 后台处理开始: {company} ({len(saved_files)}个文件)")
    # AI 解析
    for f_info in saved_files:
        try:
            entries = parse_file_with_ai(f_info["path"], f_info["name"], f_info["category"])
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            for entry in entries:
                c.execute(
                    "INSERT INTO knowledge_entries (submission_id, file_id, entry_type, title, content, metadata) VALUES (?,?,?,?,?,?)",
                    (submission_id, f_info["file_id"], entry["type"], entry["title"], entry["content"],
                     json.dumps({"source_file": f_info["name"], "category": f_info["category"]}, ensure_ascii=False))
                )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"  ⚠️ AI解析异常: {f_info['name']} - {e}")
    # 飞书同步
    try:
        sync_to_feishu(company, industry, len(saved_files), scenario, extra, saved_files)
    except Exception as e:
        print(f"  ⚠️ 飞书同步异常: {e}")
    # 秒懂推送（每公司独立知识库）
    try:
        push_to_miaodong(saved_files, company=company)
    except Exception as e:
        print(f"  ⚠️ 秒懂推送异常: {e}")
    print(f"  ✅ 后台处理完成: {company}")


@router.post("/submit")
@limiter.limit("5/minute")
async def submit_form(
    request: Request,
    background_tasks: BackgroundTasks,
    company: str = Form(...),
    industry: str = Form(...),
    scenario: str = Form(""),
    extra: str = Form(""),
    files: list[UploadFile] = File(default=[]),
    categories: str = Form("")
):
    # 输入校验
    if not company.strip():
        raise HTTPException(400, "企业名称不能为空")
    if len(company) > 100:
        raise HTTPException(400, "企业名称过长（最多100字）")
    if industry not in ALLOWED_INDUSTRIES:
        raise HTTPException(400, f"不支持的行业: {industry}")
    if len(files) > MAX_FILES_PER_SUBMISSION:
        raise HTTPException(400, f"单次最多上传 {MAX_FILES_PER_SUBMISSION} 个文件")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO submissions (company, industry, scenario, extra) VALUES (?, ?, ?, ?)",
        (company, industry, scenario, extra)
    )
    submission_id = c.lastrowid

    try:
        cat_map = json.loads(categories) if categories else {}
    except Exception:
        cat_map = {}

    company_dir = UPLOAD_DIR / sanitize_dirname(company)
    company_dir.mkdir(parents=True, exist_ok=True)

    # 同步保存文件（快速）
    saved_files = []
    for file in files:
        if not file.filename:
            continue
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(400, f"文件 {file.filename} 超过大小限制（最大 {MAX_FILE_SIZE // 1024 // 1024}MB）")
        clean_name = sanitize_filename(file.filename)
        category = cat_map.get(file.filename, "未分类")
        cat_dir = company_dir / sanitize_dirname(category)
        cat_dir.mkdir(parents=True, exist_ok=True)
        safe_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{clean_name}"
        save_path = cat_dir / safe_name
        with open(save_path, "wb") as f:
            f.write(content)
        c.execute(
            "INSERT INTO files (submission_id, category, original_name, saved_path, file_type, file_size) VALUES (?,?,?,?,?,?)",
            (submission_id, category, file.filename, str(save_path), file.content_type, len(content))
        )
        file_id = c.lastrowid
        saved_files.append({"file_id": file_id, "path": str(save_path), "name": file.filename, "category": category})

    conn.commit()
    conn.close()

    # 后台异步处理（响应发送后执行）
    background_tasks.add_task(
        process_submission, submission_id, company, industry, scenario, extra, saved_files
    )

    return {
        "success": True,
        "submission_id": submission_id,
        "company": company,
        "files_processed": len(saved_files),
        "message": "提交成功，文件正在后台处理中"
    }


@router.get("/status/{submission_id}")
async def get_submission_status(submission_id: int):
    """查询提交处理状态（无需鉴权，供客户前端轮询）"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM files WHERE submission_id = ?", (submission_id,))
    file_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM knowledge_entries WHERE submission_id = ?", (submission_id,))
    entry_count = c.fetchone()[0]
    conn.close()
    # 如果有文件但没有知识条目，说明还在处理中
    if file_count > 0 and entry_count == 0:
        status = "processing"
    elif file_count == 0:
        status = "done"  # 没有文件，不需要解析
    else:
        status = "done"
    return {"status": status, "file_count": file_count, "entry_count": entry_count}


@router.get("/submissions")
async def list_submissions(user: str = Depends(verify_admin)):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT company, industry, COUNT(*) as submit_count, MAX(created_at) as last_submit, "
        "GROUP_CONCAT(id) as submission_ids FROM submissions GROUP BY company ORDER BY last_submit DESC"
    )
    rows = [dict(r) for r in c.fetchall()]
    for row in rows:
        ids = row["submission_ids"].split(",")
        ph = ",".join("?" * len(ids))
        c.execute(f"SELECT COUNT(*) FROM files WHERE submission_id IN ({ph})", ids)
        row["file_count"] = c.fetchone()[0]
        c.execute(f"SELECT COUNT(*) FROM knowledge_entries WHERE submission_id IN ({ph})", ids)
        row["entry_count"] = c.fetchone()[0]
    conn.close()
    return {"submissions": rows}


@router.get("/knowledge/{submission_id}")
async def get_knowledge(submission_id: str, user: str = Depends(verify_admin)):
    conn = get_connection()
    c = conn.cursor()
    ids = [s.strip() for s in submission_id.split(",")]
    ph = ",".join("?" * len(ids))
    c.execute(f"SELECT * FROM knowledge_entries WHERE submission_id IN ({ph}) ORDER BY entry_type, id", ids)
    entries = [dict(r) for r in c.fetchall()]
    c.execute(f"SELECT * FROM files WHERE submission_id IN ({ph}) ORDER BY category, id", ids)
    files = [dict(r) for r in c.fetchall()]
    conn.close()
    grouped = {}
    for e in entries:
        grouped.setdefault(e["entry_type"], []).append(e)
    return {"submission_id": submission_id, "total_entries": len(entries), "files": files, "grouped": grouped}


@router.get("/file/{file_id}")
async def download_file(file_id: int, user: str = Depends(verify_admin)):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM files WHERE id = ?", (file_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "文件不存在")
    fp = Path(dict(row)["saved_path"])
    if not fp.exists():
        raise HTTPException(404, "文件已删除")
    row_dict = dict(row)
    return FileResponse(str(fp), filename=row_dict["original_name"],
                        media_type=row_dict["file_type"] or "application/octet-stream")


@router.get("/stats")
async def get_stats(user: str = Depends(verify_admin)):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM submissions")
    ts = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM files")
    tf = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM knowledge_entries")
    te = c.fetchone()[0]
    c.execute("SELECT entry_type, COUNT(*) FROM knowledge_entries GROUP BY entry_type")
    td = {r[0]: r[1] for r in c.fetchall()}
    conn.close()
    return {"total_submissions": ts, "total_files": tf, "total_knowledge_entries": te, "entry_type_distribution": td}

"""
秒懂知识库推送服务 - 每个公司独立知识库
"""
import os
import sqlite3
from pathlib import Path

import requests as req

from config import MIAODONG_ACCESS_KEY_ID, MIAODONG_ACCESS_KEY_SECRET, MIAODONG_BASE_URL, DB_PATH
from parsers import parse_pdf, parse_docx, parse_excel
from utils import retry


@retry(max_retries=2, base_delay=1.0)
def get_miaodong_token() -> str:
    """获取秒懂 API access token"""
    if not MIAODONG_ACCESS_KEY_ID or not MIAODONG_ACCESS_KEY_SECRET:
        return ""
    resp = req.post(f"{MIAODONG_BASE_URL}/get-access-token", json={
        "accessKeyId": MIAODONG_ACCESS_KEY_ID,
        "accessKeySecret": MIAODONG_ACCESS_KEY_SECRET
    }, timeout=15)
    if resp.status_code >= 500:
        raise Exception(f"秒懂服务端错误: {resp.status_code}")
    data = resp.json()
    if data.get("code") == 0 and "data" in data:
        return data["data"].get("accessToken", "")
    return ""


@retry(max_retries=2, base_delay=1.0)
def create_knowledge_base(token: str, company: str) -> str:
    """为公司创建独立知识库，返回 knowledgeBaseId"""
    resp = req.post(
        f"{MIAODONG_BASE_URL}/knowledge-base/create",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"name": company, "embeddingModelType": "text-embedding-ada-002"},
        timeout=15
    )
    if resp.status_code >= 500:
        raise Exception(f"秒懂创建知识库服务端错误: {resp.status_code}")
    data = resp.json()
    if data.get("code") == 0 and "data" in data:
        kb_id = data["data"].get("knowledgeBaseId", "")
        if kb_id:
            print(f"  ✅ 秒懂知识库创建成功: {company} (ID: {kb_id})")
            return kb_id
    print(f"  ⚠️ 秒懂知识库创建失败: {company} - {data.get('message', data.get('msg', ''))}")
    return ""


def get_or_create_kb(token: str, company: str) -> str:
    """获取公司对应的知识库 ID，不存在则创建"""
    # 先查数据库
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT kb_id FROM company_kb_map WHERE company = ?", (company,))
    row = c.fetchone()
    if row:
        conn.close()
        return row[0]

    # 不存在则创建
    kb_id = create_knowledge_base(token, company)
    if kb_id:
        c.execute("INSERT INTO company_kb_map (company, kb_id) VALUES (?, ?)", (company, kb_id))
        conn.commit()
    conn.close()
    return kb_id


def push_to_miaodong(saved_files: list, company: str = ""):
    """将文档类文件推送到该公司的秒懂知识库"""
    if not MIAODONG_ACCESS_KEY_ID or not MIAODONG_ACCESS_KEY_SECRET:
        print("  ⚠️ 秒懂未配置，跳过")
        return

    token = get_miaodong_token()
    if not token:
        return

    # 获取或创建该公司的知识库
    kb_id = get_or_create_kb(token, company)
    if not kb_id:
        print(f"  ⚠️ 秒懂跳过（无法获取知识库ID）: {company}")
        return

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    for f_info in saved_files:
        filepath = f_info.get("path", "")
        filename = f_info.get("name", "")
        category = f_info.get("category", "未分类")
        ext = Path(filename).suffix.lower()

        if ext not in (".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt", ".csv", ".md"):
            continue

        # 去重检测：同公司同文件名同大小跳过
        file_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id FROM pushed_files WHERE company=? AND filename=? AND file_size=?",
                  (company, filename, file_size))
        if c.fetchone():
            conn.close()
            print(f"  ⏭️ 秒懂跳过（重复文件）: {filename}")
            continue
        conn.close()

        try:
            content = ""
            if ext == ".pdf":
                entries = parse_pdf(filepath)
                content = "\n\n".join(e["content"] for e in entries if e["type"] != "error")
            elif ext in (".doc", ".docx"):
                entries = parse_docx(filepath)
                content = "\n\n".join(e["content"] for e in entries if e["type"] != "error")
            elif ext in (".xls", ".xlsx"):
                entries = parse_excel(filepath)
                content = "\n\n".join(e["content"] for e in entries if e["type"] != "error")
            else:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

            if not content.strip():
                print(f"  ⚠️ 秒懂跳过（无内容）: {filename}")
                continue

            resp = req.post(
                f"{MIAODONG_BASE_URL}/knowledge-base/doc/create-with-content",
                headers=headers,
                json={
                    "knowledgeBaseId": kb_id,
                    "name": filename,
                    "content": content[:50000],
                    "prefix": f"[{category}] {filename}",
                    "metadata": {"category": category, "source": "agent-form", "company": company}
                }
            )
            data = resp.json()
            if data.get("code") == 0:
                # 记录已推送，防止重复
                try:
                    conn2 = sqlite3.connect(DB_PATH)
                    conn2.execute("INSERT OR IGNORE INTO pushed_files (company, filename, file_size, kb_id) VALUES (?,?,?,?)",
                                  (company, filename, file_size, kb_id))
                    conn2.commit()
                    conn2.close()
                except Exception:
                    pass
                print(f"  ✅ 秒懂推送成功: {filename} → {company} (ID:{data['data']['id']})")
            else:
                print(f"  ⚠️ 秒懂推送失败: {filename} - {data.get('message', data.get('msg', ''))}")
        except Exception as e:
            print(f"  ⚠️ 秒懂推送异常: {filename} - {e}")

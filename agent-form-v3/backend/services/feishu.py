"""
飞书多维表格同步服务
"""
import os
from datetime import datetime

import requests as req

from config import FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_APP_TOKEN, FEISHU_TABLE_ID
from utils import retry


@retry(max_retries=2, base_delay=1.0)
def get_feishu_token() -> str | None:
    """获取飞书 tenant_access_token"""
    if not FEISHU_APP_ID or not FEISHU_APP_SECRET:
        return None
    resp = req.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET},
        timeout=15
    )
    if resp.status_code >= 500:
        raise Exception(f"飞书服务端错误: {resp.status_code}")
    data = resp.json()
    return data["tenant_access_token"] if data.get("code") == 0 else None


def upload_file_to_feishu(token: str, filepath: str, filename: str) -> str:
    """上传文件到飞书，返回 file_token"""
    with open(filepath, "rb") as f:
        resp = req.post(
            "https://open.feishu.cn/open-apis/drive/v1/medias/upload_all",
            headers={"Authorization": f"Bearer {token}"},
            data={
                "file_name": filename,
                "parent_type": "bitable_file",
                "parent_node": FEISHU_APP_TOKEN,
                "size": str(os.path.getsize(filepath))
            },
            files={"file": (filename, f, "application/octet-stream")}
        )
    data = resp.json()
    return data["data"]["file_token"] if data.get("code") == 0 else ""


def sync_to_feishu(company: str, industry: str, file_count: int,
                   scenario: str = "", extra: str = "", uploaded_files: list = None) -> bool:
    """同步提交记录到飞书多维表格"""
    if not FEISHU_APP_TOKEN or not FEISHU_TABLE_ID:
        print("  ⚠️ 飞书未配置，跳过同步")
        return False

    token = get_feishu_token()
    if not token:
        return False

    file_tokens, categories = [], []
    if uploaded_files:
        for f_info in uploaded_files:
            fp = f_info.get("path", "")
            fn = f_info.get("name", "")
            cat = f_info.get("category", "未分类")
            if fp and os.path.exists(fp):
                ft = upload_file_to_feishu(token, fp, fn)
                if ft:
                    file_tokens.append({"file_token": ft})
                    categories.append(f"{cat}: {fn}")

    record = {
        "fields": {
            "企业名称": company,
            "行业": industry,
            "提交日期": int(datetime.now().timestamp() * 1000),
            "文件数": file_count
        }
    }

    combined_scenario = (scenario.strip() if scenario else "") + \
                        ("\n\n补充：" + extra.strip() if extra and extra.strip() else "")
    if combined_scenario.strip():
        record["fields"]["场景需求"] = combined_scenario.strip()
    if file_tokens:
        record["fields"]["附件"] = file_tokens
    if categories:
        record["fields"]["附件分类"] = "\n".join(categories)

    resp = req.post(
        f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_APP_TOKEN}/tables/{FEISHU_TABLE_ID}/records",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=record
    )
    ok = resp.json().get("code") == 0
    print(f"  {'✅' if ok else '⚠️'} 飞书同步{'成功' if ok else '失败'}: {company}")
    return ok

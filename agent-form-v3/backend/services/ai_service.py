"""
AI 智能解析服务 - 使用通义千问对文本进行结构化整理
"""
import re
import json

import httpx

from config import DASHSCOPE_API_KEY, DASHSCOPE_BASE_URL, DASHSCOPE_MODEL
from parsers import parse_file
from utils import retry


@retry(max_retries=2, base_delay=2.0)
def _call_dashscope(prompt: str) -> str:
    """调用通义千问 API（带重试）"""
    resp = httpx.post(
        f"{DASHSCOPE_BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {DASHSCOPE_API_KEY}", "Content-Type": "application/json"},
        json={"model": DASHSCOPE_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.3},
        timeout=60.0
    )
    if resp.status_code >= 500:
        raise Exception(f"DashScope 服务端错误: {resp.status_code}")
    if resp.status_code != 200:
        return ""
    return resp.json()["choices"][0]["message"]["content"].strip()


def ai_parse_text(text: str, filename: str = "", category: str = "") -> list[dict]:
    """调用 AI 将原始文本整理为结构化知识条目"""
    if not text or not text.strip() or not DASHSCOPE_API_KEY:
        return []

    max_chars = 6000
    if len(text) > max_chars:
        text = text[:max_chars] + "\n...(文本过长已截断)"

    prompt = f"""你是一个知识库整理助手。请将以下内容整理为结构化的知识库条目。
要求：1.FAQ提取为type="qa" 2.流程/SOP提取为type="sop" 3.其他按主题分段type="document" 4.每条content不超过500字 5.返回纯JSON数组
文件名：{filename} 材料分类：{category}
内容：
{text}
返回JSON数组：[{{"type":"qa","title":"问题","content":"答案"}}]"""

    try:
        content = _call_dashscope(prompt)
        if not content:
            return []
        if content.startswith("```"):
            content = re.sub(r'^```\w*\n?', '', content)
            content = re.sub(r'\n?```$', '', content)
        entries = json.loads(content)
        if isinstance(entries, list):
            return [
                {"type": e["type"], "title": str(e["title"])[:200], "content": str(e["content"])[:2000]}
                for e in entries
                if isinstance(e, dict) and all(k in e for k in ("type", "title", "content"))
            ]
    except Exception as e:
        print(f"AI解析异常: {e}")
    return []


def parse_file_with_ai(filepath: str, filename: str, category: str = "") -> list[dict]:
    """先用规则解析文件，再尝试 AI 结构化整理"""
    rule_entries = parse_file(filepath, filename)

    # 图片/压缩包/未知/错误类型不需要 AI 再处理
    if rule_entries and rule_entries[0]["type"] in ("image", "archive", "unknown", "error"):
        return rule_entries
    # AI 已识别的图片内容直接返回
    if rule_entries and any("图片内容-" in e.get("title", "") for e in rule_entries):
        return rule_entries

    # 拼接所有解析出的文本
    all_text = "\n\n".join(
        f"{e['title']}:\n{e['content']}" if e['title'] != f"段落{i+1}" else e['content']
        for i, e in enumerate(rule_entries)
    )
    if not all_text.strip():
        return rule_entries

    # 尝试 AI 结构化
    ai_entries = ai_parse_text(all_text, filename, category)
    if ai_entries:
        print(f"  ✅ AI解析成功: {filename} → {len(ai_entries)}条")
        return ai_entries

    print(f"  ⚠️ AI解析失败，回退规则解析: {filename} → {len(rule_entries)}条")
    return rule_entries

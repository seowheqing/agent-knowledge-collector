"""
配置模块 - 从环境变量读取所有配置
"""
import os
from pathlib import Path

# 加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ===================== 路径配置 =====================
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
DB_PATH = BASE_DIR / "knowledge.db"
FRONTEND_DIR = BASE_DIR.parent
UPLOAD_DIR.mkdir(exist_ok=True)

# ===================== AI 模型（阿里云百炼/DashScope） =====================
DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DASHSCOPE_MODEL = "qwen-plus"

# ===================== 飞书多维表格 =====================
FEISHU_APP_ID = os.environ.get("FEISHU_APP_ID", "")
FEISHU_APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "")
FEISHU_APP_TOKEN = os.environ.get("FEISHU_APP_TOKEN", "")
FEISHU_TABLE_ID = os.environ.get("FEISHU_TABLE_ID", "")

# ===================== 秒懂知识库 =====================
MIAODONG_ACCESS_KEY_ID = os.environ.get("MIAODONG_ACCESS_KEY_ID", "")
MIAODONG_ACCESS_KEY_SECRET = os.environ.get("MIAODONG_ACCESS_KEY_SECRET", "")
MIAODONG_BASE_URL = "https://insight.juzibot.com/openapi"

# ===================== 管理后台 =====================
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "juzi2024")

# ===================== 安全配置 =====================
# CORS 允许的域名（生产环境填实际域名）
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "https://agent-knowledge-collector.onrender.com,http://localhost:8000").split(",")

# 文件上传限制
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB per file
MAX_FILES_PER_SUBMISSION = 20     # 单次最多上传文件数

# 行业白名单
ALLOWED_INDUSTRIES = {"电器", "电商", "教育", "金融", "医疗", "餐饮", "科技", "制造", "跨境", "政务", "其他"}

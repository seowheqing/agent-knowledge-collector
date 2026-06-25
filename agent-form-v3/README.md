# Agent 知识库材料收集系统

企业客户提交材料 → AI自动解析 → 结构化存储 → 同步飞书多维表格

## 快速开始

```bash
cd backend
pip install fastapi uvicorn python-multipart PyPDF2 python-docx openpyxl httpx python-dotenv
cp .env.example .env  # 填入你的密钥
python main.py
```

打开 http://localhost:8000

## 功能

- 📋 多行业材料收集表单（前端）
- 🤖 AI 智能解析（通义千问 - 文本/图片）
- 📊 飞书多维表格自动同步
- 📁 文件分类存储 + 管理后台

## 项目结构

```
agent-form-v3/
├── index2.html          # 材料收集表单
├── landing.html         # 着陆页
├── backend/
│   ├── main.py          # 后端主程序
│   ├── .env.example     # 环境变量模板
│   ├── .env             # 实际密钥（不推GitHub）
│   └── admin.html       # 管理后台（可选）
├── .gitignore
└── README.md
```

## 环境变量

| 变量 | 用途 |
|------|------|
| DASHSCOPE_API_KEY | 阿里云百炼 API Key（AI解析用） |
| FEISHU_APP_ID | 飞书应用 ID |
| FEISHU_APP_SECRET | 飞书应用密钥 |
| FEISHU_APP_TOKEN | 飞书多维表格 token |
| FEISHU_TABLE_ID | 飞书数据表 ID |

# Agent 知识库材料收集系统

企业客户提交材料 → AI自动解析 → 结构化存储 → 同步飞书多维表格 → 每公司独立秒懂知识库

## 快速开始

```bash
cd backend
pip install fastapi uvicorn python-multipart PyPDF2 python-docx openpyxl httpx python-dotenv requests slowapi
cp .env.example .env  # 填入你的密钥
python main.py
```

打开 http://localhost:8000

## 功能

- 📋 多行业材料收集表单（11个行业 + 动态材料引导）
- 🤖 AI 智能解析（通义千问 Plus 文本整理 + VL 图片识别）
- 📊 飞书多维表格自动同步（含附件上传）
- 📚 秒懂知识库自动推送（每公司独立知识库 + 文档自动分段）
- ⚡ 后台任务处理（FastAPI BackgroundTasks，用户提交秒回）
- 📁 文件分类存储 + 管理后台
- 🔒 安全防护：
  - HTTP Basic Auth 管理后台鉴权
  - CORS 白名单限制
  - 文件名/目录名消毒（防路径遍历）
  - 输入校验（文件大小、数量、行业白名单）
  - 速率限制（5次/分钟/IP）
- 🔄 外部 API 自动重试（指数退避）
- 🚫 重复文件检测（同公司同文件不重复推送）

## 项目结构

```
agent-form-v3/
├── index2.html              # 材料收集表单
├── landing.html             # 着陆页
├── backend/
│   ├── main.py              # 入口：创建 app、注册路由、启动
│   ├── config.py            # 所有配置和环境变量
│   ├── database.py          # 数据库建表和连接
│   ├── auth.py              # 认证逻辑
│   ├── parsers.py           # 文件解析器（PDF/Word/Excel/TXT/图片）
│   ├── utils.py             # 工具函数（消毒、重试装饰器）
│   ├── routes/
│   │   ├── api.py           # API 路由（submit/submissions/knowledge/stats）
│   │   └── pages.py         # 页面路由（landing/form/admin）
│   ├── services/
│   │   ├── ai_service.py    # AI 结构化解析（通义千问）
│   │   ├── feishu.py        # 飞书多维表格同步
│   │   └── miaodong.py      # 秒懂知识库推送（每公司独立）
│   ├── templates/
│   │   └── admin.html       # 管理后台页面
│   ├── .env.example         # 环境变量模板
│   └── test_main.py         # 单元测试（36个用例）
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
| MIAODONG_ACCESS_KEY_ID | 秒懂知识库 Access Key |
| MIAODONG_ACCESS_KEY_SECRET | 秒懂知识库 Secret |
| ADMIN_USERNAME | 管理后台用户名 |
| ADMIN_PASSWORD | 管理后台密码 |
| ALLOWED_ORIGINS | CORS 允许的域名（逗号分隔） |

## 测试

```bash
cd backend
pip install pytest
pytest test_main.py -v
```

## 架构

```
用户提交 → 输入校验 → 文件消毒+保存 → 立即返回成功
                                ↓ (BackgroundTasks)
                ├── AI解析（通义千问，带重试）→ 结构化存储
                ├── 飞书同步（附件+分类+需求，带重试）
                └── 秒懂推送（自动建库+去重+分段，带重试）
```

## 部署注意

- Render 免费版每次部署会清空 uploads/ 目录（文件已推送到飞书/秒懂不影响）
- 环境变量 `ALLOWED_ORIGINS` 设为你的实际域名
- 不再需要 `MIAODONG_KB_ID`（系统自动为每个公司创建独立知识库）

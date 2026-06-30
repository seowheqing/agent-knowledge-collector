# Agent 知识库材料收集系统

企业客户提交材料 → AI自动解析 → 结构化存储 → 同步飞书多维表格 → 每公司独立秒懂知识库

## 解决了什么问题

为企业搭建 AI Agent 时，最耗时的环节不是技术实现，而是**收集和整理客户的业务知识**。传统流程：

1. 反复跟客户沟通"你们需要准备哪些材料"
2. 客户零散地发来 PDF、Word、截图、聊天记录
3. 人工阅读、分类、整理成知识库格式
4. 手动录入到 AI Agent 的知识库系统

**这个项目把以上流程自动化：**

- 客户自助上传（按行业引导需要什么材料，不用来回沟通）
- AI 自动解析文档内容并结构化（省掉人工阅读整理）
- 自动同步到飞书表格（内部协作可见）
- 自动推送到 AI 知识库（Agent 即可直接使用，无需人工录入）

**从"收到客户材料"到"Agent 可用"，从原来的 1-2 天人工处理缩短到几分钟全自动完成。**

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
  - <img width="867" height="878" alt="image" src="https://github.com/user-attachments/assets/14759335-a742-4648-8753-c9161d7c21b2" />
  - <img width="772" height="902" alt="image" src="https://github.com/user-attachments/assets/5d430b35-b753-4e3b-bb9c-e5c925573e7b" />
  - <img width="982" height="566" alt="image" src="https://github.com/user-attachments/assets/5d91fd61-06bb-4a32-97a1-524a5f8c2022" />


- 🤖 AI 智能解析（通义千问 Plus 文本整理 + VL 图片识别）
- 📊 飞书多维表格自动同步（含附件上传）
  - <img width="1517" height="852" alt="image" src="https://github.com/user-attachments/assets/34212a5a-60ab-4992-aa74-94b35e8f89c4" />

- 📚 秒懂知识库自动推送（每公司独立知识库 + 文档自动分段）
  - <img width="1852" height="906" alt="image" src="https://github.com/user-attachments/assets/0c08882e-e307-4d1e-ba37-0ac7c7b2b0b6" />
  - <img width="1853" height="905" alt="image" src="https://github.com/user-attachments/assets/af9661c7-c228-4b5e-ac69-960f41b7924d" />
  - <img width="1846" height="910" alt="image" src="https://github.com/user-attachments/assets/3bcc0860-1fc7-4791-8308-a83791c2d9bf" />

- ⚡ 后台任务处理（FastAPI BackgroundTasks，用户提交秒回）
- 📁 文件分类存储 + 管理后台
  - <img width="1283" height="532" alt="image" src="https://github.com/user-attachments/assets/c64d91bb-b023-486c-89bc-8a71cc6fd3b2" />

- 🔒 安全防护：
  - HTTP Basic Auth 管理后台鉴权
  - <img width="557" height="197" alt="image" src="https://github.com/user-attachments/assets/4d47ecb9-b1c9-4d66-b2cc-0d4862190042" />

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

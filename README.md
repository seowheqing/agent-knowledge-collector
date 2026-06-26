[README.md](https://github.com/user-attachments/files/29370361/README.md)
# Agent 知识库材料收集系统

企业客户提交材料 → AI自动解析 → 结构化存储 → 同步飞书多维表格 → 推送秒懂知识库

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
- 📚 秒懂知识库自动推送（文档自动分段入库）
- ⚡ 异步处理（用户提交秒回，后台自动处理AI解析/同步/推送）
- 📁 文件分类存储 + 管理后台
- 🔒 管理后台 HTTP Basic Auth 鉴权保护
- 🛡️ 速率限制（每IP每分钟最多5次提交，防刷）

## 项目结构

```
agent-form-v3/
├── index2.html          # 材料收集表单
├── landing.html         # 着陆页
├── backend/
│   ├── main.py          # 后端主程序
│   ├── .env.example     # 环境变量模板
│   ├── .env             # 实际密钥（不推GitHub）
│   └── test_main.py     # 单元测试
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
| MIAODONG_KB_ID | 秒懂知识库 ID |
| ADMIN_USERNAME | 管理后台用户名 |
| ADMIN_PASSWORD | 管理后台密码 |

## 测试

```bash
cd backend
pip install pytest
pytest test_main.py -v
```

## 架构

```
用户提交 → 文件存本地 → 立即返回成功
                ↓ (后台异步)
        ├── AI解析（通义千问）→ 结构化存储
        ├── 飞书同步（附件+分类+需求）
        └── 秒懂推送（文档自动分段入库）
```

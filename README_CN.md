# DuckPay 后端

DuckPay 是一个现代化的支付管理系统，拥有健壮且可扩展的后端 API。

## 技术栈

- **FastAPI** - 高性能 Python Web 框架
- **SQLAlchemy** - 数据库 ORM
- **PostgreSQL** - 关系型数据库
- **JWT** - 安全令牌认证
- **SSE (Server-Sent Events)** - 实时事件流
- **Pydantic** - 数据验证和序列化

## 快速开始

### 前提条件

- Python 3.10+
- PostgreSQL 数据库
- pip 或 poetry 包管理器

### 安装

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 基于 `.env.example` 模板创建 `.env` 文件：

```bash
cp .env.example .env
```

3. 在 `.env` 文件中配置数据库连接：

```
DATABASE_URL="postgresql://username:password@localhost:5432/duckpay"
```

4. 运行数据库迁移（如果使用 Alembic）：

```bash
# 初始化 Alembic（如果尚未完成）
alembic init alembic

# 创建迁移
alembic revision --autogenerate -m "Initial migration"

# 应用迁移
alembic upgrade head
```

### 运行应用

#### 开发模式

```bash
uvicorn app.main:app --reload --port 8000
```

API 将在 `http://localhost:8000` 可用

#### 生产模式

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### API 文档

FastAPI 自动生成交互式 API 文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 项目结构

```
app/
├── api/              # API 路由
│   ├── admin.py      # 管理员端点
│   ├── categories.py # 分类端点
│   ├── records.py    # 记录端点
│   ├── status.py     # 状态端点
│   └── users.py      # 用户端点
├── crud/             # CRUD 操作
├── models/           # 数据库模型
├── schemas/          # Pydantic 模式
├── utils/            # 工具函数
│   ├── auth.py       # 认证工具
│   ├── database.py   # 数据库连接
│   └── jwt.py        # JWT 令牌处理
└── main.py           # 应用入口点
```

## 功能特性

- **用户管理** - 注册、认证和资料管理
- **支付记录** - 创建、读取、更新和删除支付记录
- **分类管理** - 管理支付分类
- **实时更新** - 使用 SSE 进行实时数据更新
- **管理员仪表板** - 管理功能
- **安全认证** - 基于 JWT 的认证和密码哈希

## 开发

### 代码风格

- 遵循 PEP 8 指南
- 为所有函数和变量使用类型提示
- 编写全面的文档字符串
- 实现适当的错误处理
- 对共享资源使用依赖注入

### 测试

```bash
# 运行测试
python -m pytest

# 运行测试并生成覆盖率报告
python -m pytest --cov=app
```

### 代码检查

```bash
# 安装代码检查工具
pip install flake8 black isort

# 运行 flake8
flake8 app

# 运行 black 格式化
black app

# 运行 isort 排序导入
isort app
```

## 许可证

MIT

---

[English Version](./README.md)
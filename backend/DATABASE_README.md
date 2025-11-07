# 数据库初始化指南

本项目使用PostgreSQL作为数据库，并通过Alembic进行数据库迁移管理。

## 前置条件

1. 安装PostgreSQL数据库
2. 创建数据库（例如：trip_master）
3. 配置数据库连接（在.env文件中或设置环境变量）
4. 安装Python依赖包

## 安装依赖

在初始化数据库之前，需要安装所有必要的Python依赖包：

```bash
cd backend
python install_requirements.py
```

或者直接使用pip安装：

```bash
cd backend
pip install -r requirements.txt
```

## 数据库配置

在项目根目录创建`.env`文件，并设置以下变量：

```
DATABASE_URL=postgresql://用户名:密码@主机:端口/数据库名
```

例如：
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/trip_master
```

## 初始化数据库

有两种方式初始化数据库：

### 方式1：使用初始化脚本

```bash
cd backend
python init_db.py
```

### 方式2：使用Alembic命令

```bash
cd backend

# 创建初始迁移
alembic revision --autogenerate -m "Initial migration"

# 应用迁移
alembic upgrade head
```

## 添加新的迁移

当修改模型后，可以创建新的迁移：

```bash
alembic revision --autogenerate -m "描述你的更改"
```

然后应用迁移：

```bash
alembic upgrade head
```

## 回滚迁移

回滚到上一个版本：

```bash
alembic downgrade -1
```

回滚到特定版本：

```bash
alembic downgrade <revision_id>
```

## 查看迁移历史

```bash
alembic history
```

## 查看当前版本

```bash
alembic current
```

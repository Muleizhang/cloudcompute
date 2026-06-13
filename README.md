# GaussOps 云资源巡检任务管理系统

本仓库用于完成“云计算技术期末实验”：使用 Docker 部署 openGauss / GaussDB，并开发、部署前后端分离 Web 应用。

## 功能

- openGauss 容器化部署，数据卷持久化。
- FastAPI 后端自动建表、写入示例数据，并提供完整 CRUD 与统计接口。
- React 前端提供任务新增、搜索、状态筛选、资源筛选、状态更新、完成标记、删除和指标展示。
- 前端、后端均提供 Dockerfile，`docker-compose.yml` 可一键启动数据库、后端和前端。
- `docs/experiment-report.md` 提供实验报告草稿，`docs/deployment.md` 提供华为云开发者空间部署步骤。

## 项目结构

```text
.
├── backend/                # FastAPI 后端
├── deploy/                 # openGauss 主备伪分布式部署脚本
├── frontend/               # React + Vite 前端
├── docs/                   # 部署说明和实验报告
├── docker-compose.yml      # openGauss + backend + frontend 编排
├── .env.example            # 环境变量模板
└── README.md
```

## 快速启动

```bash
cp .env.example .env
sudo bash deploy/setup-docker-mirror.sh   # 国内服务器需先配置 Docker 和 pip 镜像加速
docker compose up -d --build
```

如果启动时报 `failed to resolve reference`、`i/o timeout`，或 `pip install` 下载很慢，通常是服务器访问 Docker Hub / PyPI 不稳定。先执行上面的镜像加速脚本，再重新运行 `docker compose up -d --build`。

访问地址：

- 前端页面：<http://localhost:8080>
- 后端健康检查：<http://localhost:8000/api/health>
- 后端接口文档：<http://localhost:8000/docs>

## 华为云开发者空间部署

1. 创建 Linux 开发环境，确认 Docker 与 Docker Compose 可用。
2. 上传或克隆本仓库。
3. 执行：

```bash
cp .env.example .env
docker compose up -d --build
docker compose ps
```

4. 在开发者空间端口面板预览 `8080` 端口，演示前端页面。
5. 使用以下命令检查后端和数据库：

```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/tasks
curl http://localhost:8000/api/metrics
```

更详细步骤见 [docs/deployment.md](docs/deployment.md)。

如需单独展示 openGauss 伪分布式主备：

```bash
bash deploy/create-opengauss-master-standby.sh
```

## 后端接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/api/health` | 服务与数据库连通性 |
| `GET` | `/api/resource-types` | 查询资源类型 |
| `GET` | `/api/tasks` | 查询任务，支持 `keyword`、`status`、`resource_type` |
| `POST` | `/api/tasks` | 新增任务 |
| `PATCH` | `/api/tasks/{id}` | 更新任务 |
| `POST` | `/api/tasks/{id}/finish` | 标记任务完成 |
| `DELETE` | `/api/tasks/{id}` | 删除任务 |
| `GET` | `/api/metrics` | 查询统计指标 |

## 本地开发

后端：

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

前端：

```bash
cd frontend
npm install
npm run dev
```

本地开发仍需可访问的 openGauss 实例，默认连接 `localhost:5432`、用户 `gaussdb`、数据库 `postgres`。

## 提交材料

- 源代码：`backend/`、`frontend/`
- 配置文件：`docker-compose.yml`、`.env.example`、各 Dockerfile
- 部署说明：[docs/deployment.md](docs/deployment.md)
- 实验报告草稿：[docs/experiment-report.md](docs/experiment-report.md)

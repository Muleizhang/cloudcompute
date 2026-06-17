# GaussOps 云资源巡检任务管理系统

本仓库用于完成“云计算技术期末实验”：使用 Docker 部署 openGauss / GaussDB，并开发、部署前后端分离 Web 应用。

## 功能

- openGauss 容器化部署，数据卷持久化。
- FastAPI 后端自动建表、写入示例数据，并提供完整 CRUD 与统计接口。
- React 前端提供任务新增、搜索、状态筛选、资源筛选、状态更新、完成标记、删除和指标展示。
- Spark 批处理容器通过 JDBC 读取 openGauss 任务表，计算分析指标并写回 openGauss。
- 前端、后端、Spark 均提供 Dockerfile，`docker-compose.yml` 可一键启动数据库、后端、前端和 Spark 分析任务。
- `docs/experiment-report.md` 提供实验报告草稿，`docs/deployment.md` 提供华为云开发者空间部署步骤。

## 项目结构

```text
.
├── backend/                # FastAPI 后端
├── deploy/                 # openGauss 主备伪分布式部署脚本
├── frontend/               # React + Vite 前端
├── spark/                  # Spark JDBC 批处理分析任务
├── docs/                   # 部署说明和实验报告
├── docker-compose.yml      # openGauss + backend + frontend + Spark 编排
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
```

4. 在开发者空间端口面板预览 `8080` 和 `4040` 端口，分别演示前端页面和 Spark 历史管理页面。
5. 使用以下命令检查后端和数据库：

```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/tasks
curl http://localhost:8000/api/metrics
curl http://localhost:8000/api/spark-analytics/latest
```

Spark History Server 由 `spark-history` 常驻容器提供，地址为 `http://服务器公网IP:4040`，Spark 分析任务结束后页面仍可访问。

更详细步骤见 [docs/deployment.md](docs/deployment.md)。

如需单独展示 openGauss 伪分布式主备：

```bash
bash deploy/create-opengauss-master-standby.sh
```

## 服务器部署命令

首次在服务器部署：

```bash
git clone <你的仓库地址> endtermexp
cd endtermexp

cp .env.example .env
```

根据服务器端口和密码要求修改 `.env`，至少确认以下配置：

```bash
OPENGAUSS_PASSWORD=Gauss@2026
BACKEND_PORT=8000
FRONTEND_PORT=8080
OPENGAUSS_PORT=5432
SPARK_UI_PORT=4040
SPARK_WORKER_CORES=1
SPARK_WORKER_MEMORY=1g
```

构建并启动全部服务：

```bash
docker compose up -d --build
```

检查服务状态和后端连通性：

```bash
curl http://localhost:8000/api/health
```

检查 Spark 写回 openGauss 的结果：

```bash
curl http://localhost:8000/api/spark-analytics/latest
```

Spark History Server 默认映射到宿主机 `4040` 端口，由 `spark-history` 常驻容器提供，不依赖一次性分析任务是否正在运行：

```text
http://服务器公网IP:4040
```

浏览器访问：

```text
http://服务器公网IP:8080
```

以后更新部署：

```bash
cd endtermexp
git pull

docker compose up -d --build
```

华为云 ECS 或其他云服务器安全组建议：

- 放通 `8080`：前端页面访问。
- 演示 Spark 管理面板时放通 `4040`。
- `8000` 仅调试后端接口时放通，正式演示可不放通。
- `5432` 不建议公网开放，数据库应只在 Docker 内部网络访问。

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
| `GET` | `/api/spark-analytics/latest` | 查询 Spark 写回 openGauss 的最新分析快照 |

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
- 源代码：`spark/`
- 配置文件：`docker-compose.yml`、`.env.example`、各 Dockerfile
- 部署说明：[docs/deployment.md](docs/deployment.md)
- 实验报告草稿：[docs/experiment-report.md](docs/experiment-report.md)

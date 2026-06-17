# 部署说明

本项目按华为云开发者空间的容器化实验场景组织，包含 openGauss、后端 API、前端 Nginx 和 Spark 批处理分析容器。

## 1. 环境准备

1. 在华为云开发者空间创建 Linux 开发环境，确认 Docker 与 Docker Compose 可用。
2. 上传或克隆本项目代码。
3. **配置 Docker 和 pip 镜像加速器**（国内服务器必须）：

华为云开发者空间的网络访问 Docker Hub、PyPI、npm 和 Maven/JDBC 下载地址可能较慢，拉取 `enmotech/opengauss`、`python`、`node`、`nginx`、`apache/spark` 等镜像或执行 `pip install`、`npm ci` 时会超时。执行以下脚本自动配置镜像加速：

```bash
sudo bash deploy/setup-docker-mirror.sh
```

该脚本会写入 `/etc/docker/daemon.json` 和 `/etc/pip.conf`，并重启 Docker。配置完成后即可正常拉取镜像和 Python 依赖。Docker 构建后端镜像时默认使用 `.env` 中的 `PIP_INDEX_URL` 和 `PIP_TRUSTED_HOST`，也可以按需替换为其他 PyPI 镜像源。

若脚本中的镜像源失效，可手动测试可用源并替换：

```bash
docker pull docker.m.daocloud.io/enmotech/opengauss:5.0.0
```

找到可用的源后，将其写入 `/etc/docker/daemon.json` 的 `registry-mirrors` 数组，再执行 `sudo systemctl restart docker`。

4. 复制环境变量模板：

```bash
cp .env.example .env
```

`OPENGAUSS_PASSWORD` 需要满足 openGauss 口令复杂度要求，默认值为 `Gauss@2026`。

## 2. 构建并启动

```bash
docker compose up -d --build
```

> **注意**：如果构建时报 `failed to resolve reference`、`i/o timeout`，或 `pip install` 下载很慢，说明镜像加速器未配置或已失效，请回到「环境准备」第 3 步。

容器职责：

- `gaussops-opengauss`：openGauss 数据库容器，默认连接用户为 `gaussdb`，数据写入 Docker volume `opengauss_data`。
- `gaussops-backend`：FastAPI 后端，启动时自动建表并写入示例数据。
- `gaussops-frontend`：Nginx 前端容器，对外暴露 Web 页面，并将 `/api` 代理到后端容器。
- `gaussops-spark-master`：Spark Master 常驻容器，负责接收 Spark 任务提交和调度 Worker。
- `gaussops-spark-worker`：Spark Worker 常驻容器，向 Master 注册计算资源。
- `gaussops-spark-history`：Spark History Server 常驻容器，读取 Spark 事件日志并对外展示历史应用页面。
- `gaussops-spark-analytics`：Spark 批处理容器，向 Spark Master 提交任务，通过 JDBC 读取 `cloud_tasks`，计算指标后写入 `spark_task_analytics`。

Spark History Server 映射到宿主机 `4040` 端口，可通过 `http://服务器公网IP:4040` 长期访问。Spark 事件日志写入 Docker volume `spark_events`，Spark 分析任务结束后仍可在页面中查看历史应用记录。Spark 分析任务随 `docker compose up -d --build` 自动提交一次，分析结果写入 openGauss 后可由前端和后端接口读取。

## 3. 连通性测试

```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/tasks
curl http://localhost:8000/api/spark-analytics/latest
curl http://localhost:8080
curl http://localhost:4040
```

在开发者空间端口面板中开放或预览 `8080` 和 `4040` 端口，即可分别访问前端页面和 Spark 历史管理页面。

## 4. 伪分布式 openGauss 主备部署

默认 `docker-compose.yml` 提供一键演示版数据库，便于同时启动前端、后端和 openGauss。若线下检查要求展示 openGauss 伪分布式主备，可在华为云开发者空间中执行：

```bash
bash deploy/create-opengauss-master-standby.sh
docker ps
```

主库默认发布到宿主机 `5432` 端口，备库默认发布到 `6432` 端口。检查主备状态：

```bash
docker exec -it opengauss_master bash
su - omm
gs_ctl query -D /var/lib/opengauss/data
```

如需让 Web 应用连接该主库，可先不要启动默认的 `opengauss` 服务，并通过宿主机端口连接主库：

```bash
DATABASE_HOST=host.docker.internal DATABASE_PORT=5432 docker compose up -d --build --no-deps backend frontend
```

## 5. 常用运维命令

```bash
docker compose logs -f opengauss
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs spark-analytics
docker compose down
docker compose down -v
```

`docker compose down -v` 会删除 openGauss 数据卷，仅在需要清空实验数据时使用。

## 6. 单独构建镜像

```bash
docker build -t gaussops-backend:1.0 ./backend
docker build -t gaussops-frontend:1.0 ./frontend
docker build -t gaussops-spark:1.0 ./spark
```

如果课程检查要求提交镜像构建过程截图，可分别截取上述构建日志、`docker images` 输出和 `docker compose ps` 输出。

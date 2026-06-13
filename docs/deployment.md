# 部署说明

本项目按华为云开发者空间的容器化实验场景组织，包含 openGauss、后端 API、前端 Nginx 三个容器。

## 1. 环境准备

1. 在华为云开发者空间创建 Linux 开发环境，确认 Docker 与 Docker Compose 可用。
2. 上传或克隆本项目代码。
3. 复制环境变量模板：

```bash
cp .env.example .env
```

`OPENGAUSS_PASSWORD` 需要满足 openGauss 口令复杂度要求，默认值为 `Gauss@2026`。

## 2. 构建并启动

```bash
docker compose up -d --build
docker compose ps
```

容器职责：

- `gaussops-opengauss`：openGauss 数据库容器，默认连接用户为 `gaussdb`，数据写入 Docker volume `opengauss_data`。
- `gaussops-backend`：FastAPI 后端，启动时自动建表并写入示例数据。
- `gaussops-frontend`：Nginx 前端容器，对外暴露 Web 页面，并将 `/api` 代理到后端容器。

## 3. 连通性测试

```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/tasks
curl http://localhost:8080
```

在开发者空间端口面板中开放或预览 `8080` 端口即可访问前端页面。

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
docker compose down
docker compose down -v
```

`docker compose down -v` 会删除 openGauss 数据卷，仅在需要清空实验数据时使用。

## 6. 单独构建镜像

```bash
docker build -t gaussops-backend:1.0 ./backend
docker build -t gaussops-frontend:1.0 ./frontend
```

如果课程检查要求提交镜像构建过程截图，可分别截取上述构建日志、`docker images` 输出和 `docker compose ps` 输出。

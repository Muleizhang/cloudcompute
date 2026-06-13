# 《大数据与云计算技术》本科生课程实验报告

题目：基于 openGauss 的前后端分离云资源巡检任务管理系统

专业：

班级：

姓名：

学号：

武汉大学计算机学院

2026 年 6 月

## 1 概述

### 1.1 课程选题背景

本实验围绕云计算环境中的数据库容器化部署和 Web 应用容器化交付展开。系统以云资源巡检任务为业务对象，使用 openGauss / GaussDB 保存任务数据，前端负责交互展示，后端负责接口处理和数据库读写。

### 1.2 课程实验内容

实验完成了 openGauss 容器部署、FastAPI 后端开发、React 前端开发、Dockerfile 镜像构建和 Docker Compose 编排部署。应用支持任务新增、查询、筛选、状态更新、完成标记、删除和统计展示。

## 2 系统设计与实现

### 2.1 系统架构设计

系统采用前后端分离架构。前端容器运行 Nginx 并托管 React 静态资源，`/api` 请求由 Nginx 反向代理到后端容器。后端容器运行 FastAPI 服务，通过 openGauss 的 PostgreSQL 兼容协议访问数据库。基础演示环境中三个容器位于同一 Docker 网络中，数据库数据通过 Docker volume 持久化；伪分布式数据库演示环境使用一主一备 openGauss 容器部署。

### 2.2 系统技术选型

- 数据库：openGauss，容器镜像 `enmotech/opengauss:5.0.0`。
- 后端：Python、FastAPI、psycopg。
- 前端：React、TypeScript、Vite、Nginx。
- 部署：Dockerfile、Docker Compose。

### 2.3 功能模块设计与实现

后端提供健康检查、资源类型查询、任务列表查询、任务新增、任务更新、任务完成、任务删除和统计接口。前端每个筛选控件、提交按钮、状态下拉框、完成按钮和删除按钮均调用对应后端接口，数据最终写入 openGauss。

数据库表 `cloud_tasks` 包含任务标题、资源类型、负责人、优先级、状态、截止日期、描述、创建时间和更新时间字段，并建立了状态、资源类型、截止日期索引。

## 3 应用部署

### 3.1 部署 openGauss / GaussDB

在华为云开发者空间中执行：

```bash
cp .env.example .env
docker compose up -d --build opengauss
docker compose logs -f opengauss
```

openGauss 启动后监听容器内 `5432` 端口，后端通过服务名 `opengauss` 访问数据库。

如需展示伪分布式主备部署，执行：

```bash
bash deploy/create-opengauss-master-standby.sh
docker exec -it opengauss_master bash
su - omm
gs_ctl query -D /var/lib/opengauss/data
```

### 3.2 部署前端 / 后端应用

执行：

```bash
docker compose up -d --build backend frontend
docker compose ps
```

后端启动时自动创建数据表和示例数据。前端容器对外暴露 `8080` 端口，在开发者空间端口预览页面中打开即可演示。

## 4 测试评估

接口测试命令：

```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/tasks
curl http://localhost:8000/api/metrics
```

页面测试内容包括新增任务、按状态筛选、按资源类型筛选、搜索关键字、修改任务状态、标记完成和删除任务。完成这些操作后再次刷新页面，数据仍能从 openGauss 中读取，说明数据库持久化和后端读写逻辑正常。

## 5 总结

### 5.1 项目开发的挑战与应对方法

主要挑战是保证容器启动顺序和数据库可用性。后端在启动阶段加入数据库初始化重试逻辑，避免 openGauss 启动较慢导致后端立即失败。

### 5.2 项目部署存在的问题与不足

当前系统面向课程实验，未接入统一身份认证和更细粒度权限控制。部署时 openGauss 口令通过环境变量传入，生产环境应改用密钥管理服务。

### 5.3 项目展望与学习心得

后续可加入 Spark 或 Flink 批处理任务，对巡检任务和云资源运行指标进行周期性分析，并将分析结果写回 openGauss 供页面展示。

## 参考文献

1. openGauss 官方文档。
2. 华为云开发者空间相关实践文档。
3. FastAPI、React、Docker 官方文档。

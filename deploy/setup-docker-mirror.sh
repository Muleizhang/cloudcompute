#!/usr/bin/env bash
#
# 配置 Docker 和 pip 镜像加速器，解决国内服务器拉取镜像和 Python 依赖超时的问题。
#
# 用法（需要 sudo）：
#   sudo bash deploy/setup-docker-mirror.sh
#
set -euo pipefail

DAEMON_JSON="/etc/docker/daemon.json"
PIP_CONF="/etc/pip.conf"
PIP_INDEX_URL="${PIP_INDEX_URL:-https://pypi.tuna.tsinghua.edu.cn/simple}"
PIP_TRUSTED_HOST="${PIP_TRUSTED_HOST:-pypi.tuna.tsinghua.edu.cn}"

# 多个镜像源，Docker 会按顺序尝试，任意一个可用即可拉取成功。
MIRRORS=(
  "https://docker.m.daocloud.io"
  "https://docker.1panel.live"
  "https://hub.rat.dev"
)

if [ "$(id -u)" -ne 0 ]; then
  echo "请使用 sudo 运行：sudo bash deploy/setup-docker-mirror.sh"
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "未检测到 docker 命令，请先安装 Docker。"
  exit 1
fi

mkdir -p /etc/docker

# 备份已有配置
if [ -f "$DAEMON_JSON" ]; then
  cp "$DAEMON_JSON" "${DAEMON_JSON}.bak.$(date +%s)"
  echo "已备份原配置到 ${DAEMON_JSON}.bak.*"
fi

# 写入镜像加速配置
{
  echo "{"
  echo '  "registry-mirrors": ['
  for i in "${!MIRRORS[@]}"; do
    suffix=","
    if [ "$i" -eq "$((${#MIRRORS[@]} - 1))" ]; then
      suffix=""
    fi
    printf '    "%s"%s\n' "${MIRRORS[$i]}" "$suffix"
  done
  echo "  ]"
  echo "}"
} > "$DAEMON_JSON"

echo "已写入 $DAEMON_JSON"
cat "$DAEMON_JSON"

# 配置宿主机 pip 镜像。Docker 构建时还会通过 docker-compose.yml 的 build args
# 把同一个镜像源传入 backend/Dockerfile。
if [ -f "$PIP_CONF" ]; then
  cp "$PIP_CONF" "${PIP_CONF}.bak.$(date +%s)"
  echo "已备份原配置到 ${PIP_CONF}.bak.*"
fi

cat > "$PIP_CONF" <<EOF
[global]
index-url = ${PIP_INDEX_URL}
trusted-host = ${PIP_TRUSTED_HOST}
timeout = 120
disable-pip-version-check = true
EOF

echo "已写入 $PIP_CONF"
cat "$PIP_CONF"

# 重启 Docker 守护进程
if command -v systemctl >/dev/null 2>&1; then
  systemctl daemon-reload
  systemctl restart docker
  echo "Docker 已重启。"
else
  echo "未检测到 systemctl，请手动重启 Docker 服务后继续。"
fi

echo ""
echo "验证加速器是否生效："
docker info 2>/dev/null | grep -A 5 "Registry Mirrors" || true

echo ""
echo "测试拉取 openGauss 镜像："
docker pull enmotech/opengauss:5.0.0 && echo "拉取成功！" || echo "拉取失败，请尝试更换镜像源。"

echo ""
echo "当前 pip 镜像源："
python3 -m pip config list 2>/dev/null || true

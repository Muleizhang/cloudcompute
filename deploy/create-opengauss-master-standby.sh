#!/usr/bin/env bash
set -euo pipefail

OG_NETWORK="${OG_NETWORK:-gaussops-opengauss-ha}"
OG_SUBNET="${OG_SUBNET:-172.11.0.0/24}"
OG_VERSION="${OG_VERSION:-5.0.0}"
GS_PASSWORD="${GS_PASSWORD:-${OPENGAUSS_PASSWORD:-Gauss@2026}}"

MASTER_IP="${MASTER_IP:-172.11.0.101}"
STANDBY_IP="${STANDBY_IP:-172.11.0.102}"
MASTER_HOST_PORT="${MASTER_HOST_PORT:-5432}"
MASTER_LOCAL_PORT="${MASTER_LOCAL_PORT:-5434}"
STANDBY_HOST_PORT="${STANDBY_HOST_PORT:-6432}"
STANDBY_LOCAL_PORT="${STANDBY_LOCAL_PORT:-6434}"
MASTER_NODENAME="${MASTER_NODENAME:-opengauss_master}"
STANDBY_NODENAME="${STANDBY_NODENAME:-opengauss_standby1}"
STANDBY_DELAY_SECONDS="${STANDBY_DELAY_SECONDS:-30}"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker command not found"
  exit 1
fi

if docker container inspect "$MASTER_NODENAME" >/dev/null 2>&1; then
  echo "container $MASTER_NODENAME already exists"
  exit 1
fi

if docker container inspect "$STANDBY_NODENAME" >/dev/null 2>&1; then
  echo "container $STANDBY_NODENAME already exists"
  exit 1
fi

if ! docker network inspect "$OG_NETWORK" >/dev/null 2>&1; then
  docker network create --subnet="$OG_SUBNET" "$OG_NETWORK"
fi

docker run \
  --network "$OG_NETWORK" \
  --ip "$MASTER_IP" \
  --privileged=true \
  -u root \
  --name "$MASTER_NODENAME" \
  -h "$MASTER_NODENAME" \
  -p "$MASTER_HOST_PORT:$MASTER_HOST_PORT" \
  -e GS_PORT="$MASTER_HOST_PORT" \
  -e GS_USERNAME=gaussdb \
  -e GS_PASSWORD="$GS_PASSWORD" \
  -e NODE_NAME="$MASTER_NODENAME" \
  -e OG_SUBNET="$OG_SUBNET" \
  -e REPL_CONN_INFO="replconninfo1 = 'localhost=$MASTER_IP localport=$MASTER_LOCAL_PORT localservice=$MASTER_HOST_PORT remotehost=$STANDBY_IP remoteport=$STANDBY_LOCAL_PORT remoteservice=$STANDBY_HOST_PORT'\n" \
  -d "enmotech/opengauss:$OG_VERSION" \
  -M primary

echo "waiting ${STANDBY_DELAY_SECONDS}s for primary initialization"
sleep "$STANDBY_DELAY_SECONDS"

docker run \
  --network "$OG_NETWORK" \
  --ip "$STANDBY_IP" \
  --privileged=true \
  -u root \
  --name "$STANDBY_NODENAME" \
  -h "$STANDBY_NODENAME" \
  -p "$STANDBY_HOST_PORT:$STANDBY_HOST_PORT" \
  -e GS_PORT="$STANDBY_HOST_PORT" \
  -e GS_USERNAME=gaussdb \
  -e GS_PASSWORD="$GS_PASSWORD" \
  -e NODE_NAME="$STANDBY_NODENAME" \
  -e OG_SUBNET="$OG_SUBNET" \
  -e REPL_CONN_INFO="replconninfo1 = 'localhost=$STANDBY_IP localport=$STANDBY_LOCAL_PORT localservice=$STANDBY_HOST_PORT remotehost=$MASTER_IP remoteport=$MASTER_LOCAL_PORT remoteservice=$MASTER_HOST_PORT'\n" \
  -d "enmotech/opengauss:$OG_VERSION" \
  -M standby

cat <<INFO
openGauss master-standby containers started.

Primary:
  container: $MASTER_NODENAME
  host port: $MASTER_HOST_PORT

Standby:
  container: $STANDBY_NODENAME
  host port: $STANDBY_HOST_PORT

Verify replication:
  docker exec -it $MASTER_NODENAME bash
  su - omm
  gs_ctl query -D /var/lib/opengauss/data
INFO


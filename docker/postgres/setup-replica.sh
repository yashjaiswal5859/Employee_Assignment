#!/bin/bash
set -e

# Ensure the PGDATA directory exists
mkdir -p "$PGDATA"

if [ ! -s "$PGDATA/PG_VERSION" ]; then
  echo ">>> Replica data directory does not contain PG_VERSION, initializing replication..."

  # Clear existing files in PGDATA to avoid pg_basebackup conflicts
  rm -rf "$PGDATA"/*

  until pg_isready -h "$MASTER_HOST" -p "$MASTER_PORT" -U "$REPLICATION_USER"; do
    echo ">>> Waiting for master at $MASTER_HOST:$MASTER_PORT..."
    sleep 2
  done

  echo ">>> Taking base backup from master..."
  PGPASSWORD="$REPLICATION_PASSWORD" pg_basebackup -h "$MASTER_HOST" -p "$MASTER_PORT" -D "$PGDATA" -U "$REPLICATION_USER" -v -P --wal-method=stream

  echo ">>> Writing replication configuration..."
  cat >> "$PGDATA/postgresql.conf" <<EOF
primary_conninfo = 'host=$MASTER_HOST port=$MASTER_PORT user=$REPLICATION_USER password=$REPLICATION_PASSWORD'
primary_slot_name = '${REPLICATION_SLOT:-replica_slot}'
hot_standby = on
EOF

  touch "$PGDATA/standby.signal"
  chown -R postgres:postgres "$PGDATA"
fi

echo ">>> Starting PostgreSQL replica..."
exec docker-entrypoint.sh postgres

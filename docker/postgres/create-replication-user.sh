#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
CREATE ROLE ${REPLICATION_USER:-replicator} REPLICATION LOGIN ENCRYPTED PASSWORD '${REPLICATION_PASSWORD:-secret123}';
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_replication_slots WHERE slot_name = '${REPLICATION_SLOT:-replica_slot}') THEN
        PERFORM pg_create_physical_replication_slot('${REPLICATION_SLOT:-replica_slot}');
    END IF;
END \$\$;
EOSQL

cat >> "$PGDATA/pg_hba.conf" <<-EOF
host replication ${REPLICATION_USER:-replicator} 0.0.0.0/0 trust
EOF

pg_ctl reload -D "$PGDATA"

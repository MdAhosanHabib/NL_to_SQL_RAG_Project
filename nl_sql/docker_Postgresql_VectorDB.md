[root@de ~]# mkdir -p /u01/nl_sql
[root@de ~]# cd /u01/nl_sql

dnf install -y yum-utils
dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo

dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

systemctl enable --now docker

systemctl status docker
docker version

[root@de ~]# mkdir -p /u01/nl_sql/aidb
[root@de ~]# cd /u01/nl_sql/aidb

cat << 'EOF' > docker-compose.yml
services:
  pg-vector-db:
    image: pgvector/pgvector:pg18
    container_name: pg-vector-db
    restart: always
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: banking_db
    ports:
      - "5432:5432"
    volumes:
      # Persistent storage for the database
      - pgvector_data:/var/lib/postgresql

volumes:
  pgvector_data:
EOF

[root@de ~]# docker compose up -d
[root@de aidb]# docker exec -it pg-vector-db psql -U admin -d banking_db
banking_db=# CREATE EXTENSION IF NOT EXISTS vector;

[root@de ~]# mkdir -p /u01/nl_sql/banking_rag/sql
[root@de ~]# cd /u01/nl_sql/banking_rag/sql
[root@de sql]# ll
total 8
-rw-r--r-- 1 root root 1592 Jun  6 15:46 01_schema.sql
-rw-r--r-- 1 root root 3708 Jun  6 15:46 02_seed_data.sql
[root@de sql]#

[root@de sql]# docker exec -i pg-vector-db psql -U admin -d banking_db < 01_schema.sql
[root@de sql]# docker exec -it pg-vector-db psql -U admin -d banking_db -c "\dt"
[root@de sql]# docker exec -i pg-vector-db psql -U admin -d banking_db < 02_seed_data.sql

-- check vector data after push from langchain
[root@de aidb]# docker exec -it pg-vector-db psql -U admin -d banking_db
SELECT 
    cmetadata->>'name' AS schema_name, 
    cmetadata->>'type' AS doc_type, 
    SUBSTRING(document, 1, 60) || '...' AS preview_text 
FROM langchain_pg_embedding;


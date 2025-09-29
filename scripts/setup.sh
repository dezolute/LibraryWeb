#!/bin/bash

set -e

docker compose -f ./docker-compose.yml -p libraryweb up -d
sleep 1
docker compose logs
sleep 1
docker compose exec api alembic upgrade head
echo -e "\n\nSERVER START\nAPI url: http://127.0.0.1:8000\nDOCS url: http://127.0.0.1:8000/docs\n\n"
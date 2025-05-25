#!/bin/bash

FILENAME=$1
echo $FILENAME
docker compose cp backend:${FILENAME} ./app/alembic/versions/

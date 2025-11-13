#!/bin/bash

# Указываем явный путь к alembic.ini
poetry run alembic -c /app/alembic.ini revision --autogenerate -m "Create users table"
poetry run alembic -c /app/alembic.ini upgrade head
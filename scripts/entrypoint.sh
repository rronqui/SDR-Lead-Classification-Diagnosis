#!/bin/bash
set -e

echo "Esperando PostgreSQL estar pronto..."
until pg_isready -h postgres -U postgres; do
  echo "Aguardando banco..."
  sleep 2
done

echo "Banco pronto! Executando migrations..."
alembic upgrade head

echo "Iniciando aplicação..."
exec "$@"
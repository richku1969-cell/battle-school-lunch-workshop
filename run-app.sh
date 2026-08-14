#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir"

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example. Update NEIS_API_KEY in .env if needed."
fi

if ! docker info >/dev/null 2>&1; then
  echo "Docker Desktop or the Docker engine is not running. Start Docker first, then run ./run-app.sh again." >&2
  exit 1
fi

docker compose up --build

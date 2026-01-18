#!/bin/bash
# Run tests inside Docker container

docker compose run --rm ml_service sh -c "pip install -q pytest pytest-asyncio httpx && pytest tests/ -v $*"

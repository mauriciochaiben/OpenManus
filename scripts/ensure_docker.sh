#!/bin/bash

# Script to ensure Docker is running before running tests or other Docker-dependent operations
# This prevents Docker-related test failures due to Docker daemon not being started

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🐳 Checking Docker status..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed. Please install Docker Desktop."
    echo "   Download from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "📦 Docker daemon is not running. Starting Docker Desktop..."

    # Try to start Docker Desktop on macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if [ -d "/Applications/Docker.app" ]; then
            open /Applications/Docker.app
            echo "⏳ Waiting for Docker Desktop to start..."

            # Wait up to 60 seconds for Docker to start
            for i in {1..60}; do
                if docker info &> /dev/null; then
                    echo "✅ Docker is now running!"
                    break
                fi
                echo "   Waiting... ($i/60)"
                sleep 1
            done

            # Final check
            if ! docker info &> /dev/null; then
                echo "❌ Error: Docker failed to start within 60 seconds."
                echo "   Please start Docker Desktop manually and try again."
                exit 1
            fi
        else
            echo "❌ Error: Docker Desktop not found in /Applications/Docker.app"
            echo "   Please install Docker Desktop and try again."
            exit 1
        fi
    else
        echo "❌ Error: Docker daemon is not running."
        echo "   Please start Docker manually and try again."
        exit 1
    fi
else
    echo "✅ Docker is already running!"
fi

# Check if required images are available
echo "🔍 Checking required Docker images..."

REQUIRED_IMAGES=(
    "python:3.12-slim"
)

for image in "${REQUIRED_IMAGES[@]}"; do
    if ! docker image inspect "$image" &> /dev/null; then
        echo "📥 Pulling required image: $image"
        docker pull "$image"
    else
        echo "✅ Image available: $image"
    fi
done

echo "🎉 Docker environment is ready!"

# If arguments are provided, execute them
if [ $# -gt 0 ]; then
    echo "🚀 Executing: $@"
    exec "$@"
fi

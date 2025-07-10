#!/bin/bash
# Podman convenience scripts for data-parser

# Build the application
build() {
    echo "Building with Podman (extended timeout)..."
    podman build  --no-cache -t data-parser .
}

# Run development server
dev() {
    echo "Starting development server with Podman..."
    podman-compose -f podman-compose.yml up web
}

# Run production server
prod() {
    echo "Starting production server with Podman..."
    podman-compose -f podman-compose.yml up prod
}

# Run tests
test() {
    echo "Running tests with Podman..."
    podman-compose -f podman-compose.yml run test
}

# Stop all containers
stop() {
    echo "Stopping all containers..."
    podman-compose -f podman-compose.yml down
}

# Clean up containers and images
clean() {
    echo "Cleaning up Podman containers and images..."
    podman container prune -f
    podman image prune -f
}

# Show running containers
ps() {
    echo "Running Podman containers:"
    podman ps
}

# Show logs
logs() {
    echo "Container logs:"
    podman-compose -f podman-compose.yml logs -f
}

# Help
help() {
    echo "Available commands:"
    echo "  build  - Build the application image"
    echo "  dev    - Start development server"
    echo "  prod   - Start production server"
    echo "  test   - Run tests"
    echo "  stop   - Stop all containers"
    echo "  clean  - Clean up containers and images"
    echo "  ps     - Show running containers"
    echo "  logs   - Show container logs"
    echo "  help   - Show this help"
}

# Run the specified command
case "$1" in
    build) build ;;
    dev) dev ;;
    prod) prod ;;
    test) test ;;
    stop) stop ;;
    clean) clean ;;
    ps) ps ;;
    logs) logs ;;
    help|*) help ;;
esac

#!/bin/bash

# Define usage instructions
usage() {
    echo "Usage: $0 {start|stop|restart|logs|status|prune|remove|down|rebuild}"
    echo ""
    echo "Commands:"
    echo "  start       - Start all services"
    echo "  stop        - Stop running services"
    echo "  restart     - Restart all services"
    echo "  logs        - View logs of all services"
    echo "  status      - Show running containers"
    echo "  prune       - Remove unused containers, networks, and volumes"
    echo "  remove      - Remove all containers"
    echo "  down        - Stop and remove containers, networks, and volumes"
    echo "  rebuild     - Rebuild and restart services"
    exit 1
}

# Ensure .env is loaded
if [ -f backend/.env ]; then
    export $(grep -v '^#' backend/.env | xargs)
fi

# Check if user provided an argument
if [ $# -eq 0 ]; then
    usage
fi

# Get command argument
COMMAND=$1

# Execute based on command
case "$COMMAND" in
    start)
        echo "Starting all services..."
        docker compose up -d
        ;;
    stop)
        echo "Stopping all running services..."
        docker compose stop
        ;;
    restart)
        echo "Restarting all services..."
        docker compose restart
        ;;
    logs)
        echo "Viewing logs (use Ctrl+C to exit)..."
        docker compose logs -f
        ;;
    status)
        echo "Checking running containers..."
        docker ps
        ;;
    prune)
        echo "Removing unused Docker resources..."
        docker system prune -af
        ;;
    remove)
        echo "Removing all containers..."
        docker rm -f $(docker ps -aq)
        ;;
    down)
        echo "Stopping and removing all services..."
        docker compose down -v
        ;;
    rebuild)
        echo "Rebuilding and restarting services..."
        docker compose up --build -d
        ;;
    *)
        usage
        ;;
esac

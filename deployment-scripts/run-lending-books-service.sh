#!/bin/bash

set -e

# Configuration
NETWORK_NAME=librarypal-net
VOLUME_NAME=librarypal_mysql_data

DB_CONTAINER=librarypal-db
DB_IMAGE=mysql:8.0
DB_PORT=3306
DB_ROOT_PASSWORD=admin123
DB_NAME=library

PMA_CONTAINER=librarypal-db-admin
PMA_IMAGE=phpmyadmin
PMA_PORT=8080

USER_CONTAINER=librarypal-lending-books-service-container
USER_IMAGE=librarypal-lending-books-service
USER_PORT=8002

DEPENDENT_CONTAINERS=("librarypal-users-service-container" "librarypal-books-service-container")  # List of dependent containers

# MySQL env vars for user-service
DB_USER=root
DB_PASSWORD=$DB_ROOT_PASSWORD
DB_HOST=$DB_CONTAINER

# Create network and volume if not exist
echo "➡️  Creating Docker network and volume if not exists..."
docker network inspect $NETWORK_NAME >/dev/null 2>&1 || docker network create $NETWORK_NAME
docker volume inspect $VOLUME_NAME >/dev/null 2>&1 || docker volume create $VOLUME_NAME

# Start MySQL container if not running
if [ "$(docker ps -q -f name=$DB_CONTAINER)" ]; then
  echo "🐬 MySQL container '$DB_CONTAINER' is already running."
else
  if [ "$(docker ps -aq -f name=$DB_CONTAINER)" ]; then
    echo "🐬 Starting existing MySQL container..."
    docker start $DB_CONTAINER
  else
    echo "🐬 Running new MySQL container..."
    docker run -d \
      --name $DB_CONTAINER \
      --network $NETWORK_NAME \
      -e MYSQL_ROOT_PASSWORD=$DB_ROOT_PASSWORD \
      -e MYSQL_DATABASE=$DB_NAME \
      -v $VOLUME_NAME:/var/lib/mysql \
      -p $DB_PORT:3306 \
      $DB_IMAGE
  fi
fi

# Start phpMyAdmin container if not running
if [ "$(docker ps -q -f name=$PMA_CONTAINER)" ]; then
  echo "🧰 phpMyAdmin container '$PMA_CONTAINER' is already running."
else
  if [ "$(docker ps -aq -f name=$PMA_CONTAINER)" ]; then
    echo "🧰 Starting existing phpMyAdmin container..."
    docker start $PMA_CONTAINER
  else
    echo "🧰 Running new phpMyAdmin container..."
    docker run -d \
      --name $PMA_CONTAINER \
      --network $NETWORK_NAME \
      -e PMA_HOST=$DB_CONTAINER \
      -e PMA_PORT=3306 \
      -e MYSQL_ROOT_PASSWORD=$DB_ROOT_PASSWORD \
      -p $PMA_PORT:80 \
      $PMA_IMAGE
  fi
fi

# Check if all dependent containers are running
echo "🔍 Checking dependent containers' running status..."

for DEP_CONTAINER in "${DEPENDENT_CONTAINERS[@]}"; do
  echo "Checking if container '$DEP_CONTAINER' is running..."

  # Check if the dependent container is running
  DEP_CONTAINER_RUNNING=$(docker ps -q -f name=$DEP_CONTAINER)

  if [ -z "$DEP_CONTAINER_RUNNING" ]; then
    echo "❌ Error: '$DEP_CONTAINER' is not running."
    exit 1
  else
    echo "✅ '$DEP_CONTAINER' is running."
  fi
done

# Always rebuild and restart lending-books-service container
echo "🧹 Stopping old lending-books-service container (if any)..."
docker rm -f $USER_CONTAINER 2>/dev/null || true

echo "🔨 Building lending-books-service image..."
docker build -t $USER_IMAGE .

echo "🚀 Starting lending-books-service container..."
docker run -d \
  --name $USER_CONTAINER \
  --network $NETWORK_NAME \
  -e DB_USER=$DB_USER \
  -e DB_PASSWORD=$DB_PASSWORD \
  -e DB_HOST=$DB_HOST \
  -e DB_NAME=$DB_NAME \
  -e USER_AUTH_SERVICE_URL=http://host.docker.internal:8000 \
  -e BOOK_SERVICE_URL=http://host.docker.internal:8001 \
  -p $USER_PORT:$USER_PORT \
  $USER_IMAGE

echo "✅ All services are up:"
echo "- MySQL:         localhost:$DB_PORT"
echo "- phpMyAdmin:    http://localhost:$PMA_PORT"
echo "- LendingBooks Service:  http://localhost:$USER_PORT/docs"
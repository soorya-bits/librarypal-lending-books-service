@echo off
setlocal enabledelayedexpansion

:: Configuration
set NETWORK_NAME=librarypal-net
set VOLUME_NAME=librarypal_mysql_data

set DB_CONTAINER=librarypal-db
set DB_IMAGE=mysql:8.0
set DB_PORT=3306
set DB_ROOT_PASSWORD=admin123
set DB_NAME=library

set PMA_CONTAINER=librarypal-db-admin
set PMA_IMAGE=phpmyadmin
set PMA_PORT=8080

set USER_CONTAINER=librarypal-lending-books-service-container
set USER_IMAGE=librarypal-lending-books-service
set USER_PORT=8002

set DEPENDENT_CONTAINERS=librarypal-users-service-container librarypal-books-service-container

:: MySQL env vars for user-service
set DB_USER=root
set DB_PASSWORD=%DB_ROOT_PASSWORD%
set DB_HOST=%DB_CONTAINER%

:: Create network and volume if not exist
echo ➡️  Creating Docker network and volume if not exists...
docker network inspect %NETWORK_NAME% >nul 2>&1 || docker network create %NETWORK_NAME%
docker volume inspect %VOLUME_NAME% >nul 2>&1 || docker volume create %VOLUME_NAME%

:: Start MySQL container if not running
for /f %%i in ('docker ps -q -f name=%DB_CONTAINER%') do set DB_RUNNING=%%i
if defined DB_RUNNING (
    echo 🐬 MySQL container '%DB_CONTAINER%' is already running.
) else (
    for /f %%i in ('docker ps -aq -f name=%DB_CONTAINER%') do set DB_EXISTS=%%i
    if defined DB_EXISTS (
        echo 🐬 Starting existing MySQL container...
        docker start %DB_CONTAINER%
    ) else (
        echo 🐬 Running new MySQL container...
        docker run -d ^
          --name %DB_CONTAINER% ^
          --network %NETWORK_NAME% ^
          -e MYSQL_ROOT_PASSWORD=%DB_ROOT_PASSWORD% ^
          -e MYSQL_DATABASE=%DB_NAME% ^
          -v %VOLUME_NAME%:/var/lib/mysql ^
          -p %DB_PORT%:3306 ^
          %DB_IMAGE%
    )
)

:: Start phpMyAdmin container if not running
for /f %%i in ('docker ps -q -f name=%PMA_CONTAINER%') do set PMA_RUNNING=%%i
if defined PMA_RUNNING (
    echo 🧰 phpMyAdmin container '%PMA_CONTAINER%' is already running.
) else (
    for /f %%i in ('docker ps -aq -f name=%PMA_CONTAINER%') do set PMA_EXISTS=%%i
    if defined PMA_EXISTS (
        echo 🧰 Starting existing phpMyAdmin container...
        docker start %PMA_CONTAINER%
    ) else (
        echo 🧰 Running new phpMyAdmin container...
        docker run -d ^
          --name %PMA_CONTAINER% ^
          --network %NETWORK_NAME% ^
          -e PMA_HOST=%DB_CONTAINER% ^
          -e PMA_PORT=3306 ^
          -e MYSQL_ROOT_PASSWORD=%DB_ROOT_PASSWORD% ^
          -p %PMA_PORT%:80 ^
          %PMA_IMAGE%
    )
)

:: Check if all dependent containers are running
echo 🔍 Checking dependent containers' running status...
for %%i in (%DEPENDENT_CONTAINERS%) do (
    echo Checking if container '%%i' is running...
    for /f %%j in ('docker ps -q -f name=%%i') do set DEP_CONTAINER_RUNNING=%%j
    if not defined DEP_CONTAINER_RUNNING (
        echo ❌ Error: '%%i' is not running.
        exit /b 1
    ) else (
        echo ✅ '%%i' is running.
    )
)

:: Always rebuild and restart lending-books-service container
echo 🧹 Stopping old lending-books-service container (if any)...
docker rm -f %USER_CONTAINER% 2>nul || echo No previous container to remove.

echo 🔨 Building lending-books-service image...
docker build -t %USER_IMAGE% .

echo 🚀 Starting lending-books-service container...
docker run -d ^
  --name %USER_CONTAINER% ^
  --network %NETWORK_NAME% ^
  -e DB_USER=%DB_USER% ^
  -e DB_PASSWORD=%DB_PASSWORD% ^
  -e DB_HOST=%DB_HOST% ^
  -e DB_NAME=%DB_NAME% ^
  -e USER_AUTH_SERVICE_URL=http://host.docker.internal:8000 ^
  -e BOOKS_SERVICE_URL=http://host.docker.internal:8001 ^
  -p %USER_PORT%:%USER_PORT% ^
  %USER_IMAGE%

echo ✅ All services are up:
echo - MySQL:         localhost:%DB_PORT%
echo - phpMyAdmin:    http://localhost:%PMA_PORT%
echo - LendingBooks Service:  http://localhost:%USER_PORT%/docs

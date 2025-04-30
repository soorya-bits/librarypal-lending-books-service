# Lending Books Service

This application is a microservice that manages book lending operations such as lending, returning, and tracking borrowed books. It is designed to be lightweight, scalable, and easy to integrate with other services.

## Features
- Book lending and return management
- RESTful API endpoints
- Lightweight and containerized for easy deployment

## Prerequisites
- Docker installed on your system
- Basic knowledge of Docker commands

## Running the Application in Docker

### Steps for Windows and Mac:

1. Clone the repository:
  ```bash
  git clone https://github.com/soorya-bits/learningpal-lending-books-service.git
  cd lending-books-service
  ```

2. Run the appropriate script based on your operating system:
   - **For Windows**: Run the `run-lending-service.bat` script:
   ```cmd
   ./deploymet-scripts/run-lending-service.bat
   ```
   - **For macOS**: Run the `run-lending-service.sh` script:
   ```bash
   ./deploymet-scripts/run-lending-service.sh
   ```

3. Access the application:
  Open your browser and navigate to `http://localhost:8002/docs`.

## Notes
- Ensure Docker Desktop is running on your system.

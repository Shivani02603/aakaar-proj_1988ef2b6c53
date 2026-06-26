# Install dependencies for both backend and frontend
install:
	pip install -r backend/requirements.txt
	cd frontend && npm install

# Start development environment
dev:
	./scripts/dev.sh

# Build production-ready Docker images
build:
	docker-compose build

# Run tests for backend and frontend
test:
	pytest backend/tests
	cd frontend && npm test

# Start all services using Docker Compose
docker-up:
	docker-compose up -d

# Stop all services using Docker Compose
docker-down:
	docker-compose down

# Clean up Docker containers, images, and volumes
clean:
	docker-compose down -v
	docker system prune -f
# UniLink Setup Guide

## Current Status
✅ **Frontend**: React app running on port 5000 (fully styled with modern UI)
❌ **Backend**: Python FastAPI (requires external services)
⚙️ **Microservice**: Go notification service (needs configuration)

## Backend Setup (Python FastAPI)
**Location**: `app/` directory  
**Framework**: FastAPI on port 3001

### Prerequisites Required
The Python backend requires these services to run:

1. **MongoDB** - User & post data
   ```
   mongodb://localhost:27017
   ```

2. **Redis** - Caching & sessions
   ```
   redis://localhost:6379
   ```

3. **PostgreSQL** - For notification service integration
   ```
   postgresql://user:password@localhost:5432/unilink
   ```

### To Run Locally
```bash
cd app
pip install -r requirements.txt
PYTHONPATH=. python -m uvicorn main:app --host 0.0.0.0 --port 3001 --reload
```

### Environment Variables
Create a `.env` file:
```env
MONGODB_URI=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://user:password@localhost:5432/unilink
JWT_SECRET=your-secret-key
CLIENT_URL=http://localhost:5000
S3_BUCKET=unilink
AWS_REGION=us-east-1
NOTIFICATION_SERVICE_URL=http://localhost:8080
```

## Go Microservice (Notification Service)
**Location**: `notification-service/` directory  
**Language**: Go 1.21+
**Port**: 8080

### To Run Locally
```bash
cd notification-service
go mod download
go run ./cmd/server/main.go
```

### Environment Variables
The service uses:
- PostgreSQL (for notifications)
- Redis (for WebSocket pub/sub)
- Configuration in `internal/config/config.go`

## API Endpoints

### Python Backend
- `GET /` - Health check
- `POST /auth/login` - Login
- `POST /auth/register` - Register
- `GET /users/{userId}` - Get user profile
- `POST /posts` - Create post
- `GET /posts` - Get feed

### Go Notification Service
- `POST /notifications` - Create notification
- `GET /notifications/{userId}` - Get user notifications
- `WS /ws/{userId}` - WebSocket connection

## Frontend Configuration
The React app is already configured to:
- Communicate with backend at `http://localhost:3001` (configured in `client/src/config/api.js`)
- Use WebSocket for real-time notifications

## Quick Start (With Services Available)
```bash
# Terminal 1: Frontend
cd client && npm start

# Terminal 2: Python Backend
cd app && python -m uvicorn main:app --reload --port 3001

# Terminal 3: Go Notification Service  
cd notification-service && go run ./cmd/server/main.go
```

## Deployed Frontend
Available at: `http://localhost:5000`

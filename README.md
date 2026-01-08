# 🎓 UniLink Backend

A comprehensive microservices-based backend for a university social networking platform built with FastAPI, Go, MongoDB, and Redis.

## 📋 Table of Contents

- [Architecture](#architecture)
- [Services](#services)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

---

## 🏗️ Architecture

<img width="1536" height="1024" alt="unilink-arch" src="https://github.com/user-attachments/assets/b5b8b1ad-4e21-437e-9dfa-0dfcf7c2c534" />

---

## 🚀 Services

### 1. Main API (FastAPI - Python)
**Port:** 3001

**Responsibilities:**
- User authentication & authorization (JWT)
- User profile management
- Post creation & feed management
- Friend connections
- S3 file uploads
- Email OTP verification
- Discord OAuth integration
- AI-powered caption generation

**Key Features:**
- JWT-based authentication
- Password hashing with bcrypt
- Discord OAuth2 integration
- AWS S3 presigned URLs
- Google Gemini API for captions
- Redis pub/sub for notifications

### 2. Chat Service (FastAPI - Python)
**Port:** 4000

**Responsibilities:**
- Real-time messaging via Socket.IO
- Conversation management
- Message history
- Online/offline status
- Typing indicators
- Read receipts
- Message caching

**Key Features:**
- WebSocket support with Socket.IO
- JWT authentication for WebSockets
- Redis pub/sub for multi-instance support
- Message caching in Redis
- MongoDB for persistence

### 3. Notification Service (Go)
**Port:** 8080

**Responsibilities:**
- Real-time notification delivery
- Notification grouping & deduplication
- User preferences management
- WebSocket connections
- Statistics & analytics

**Key Features:**
- WebSocket real-time updates
- Redis Streams for queue processing
- Notification grouping (e.g., "John and 5 others liked your post")
- Priority-based processing
- Quiet hours support
- Per-notification-type preferences

---

## 🛠️ Tech Stack

### Languages & Frameworks
- **Python 3.11+** - Main API & Chat Service
- **Go 1.23+** - Notification Service
- **FastAPI** - REST API framework
- **Socket.IO** - Real-time communication

### Databases & Caching
- **MongoDB** - Primary database
- **Redis** - Caching, pub/sub, presence

### External Services
- **AWS S3** - File storage
- **Google Gemini** - AI captions
- **Discord OAuth** - Social login
- **Gmail SMTP** - Email OTP

### Key Libraries
- **FastAPI** - Web framework
- **Motor** - Async MongoDB driver
- **Socket.IO** - WebSocket support
- **Redis** - Caching & pub/sub
- **Pydantic** - Data validation
- **JWT** - Token authentication
- **Gin** - Go web framework
- **Gorilla WebSocket** - Go WebSocket

---

## 📦 Prerequisites

### Required Software
- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Go 1.23+** ([Download](https://golang.org/dl/))
- **MongoDB 6.0+** ([Download](https://www.mongodb.com/try/download/community))
- **Redis 7.0+** ([Download](https://redis.io/download))

### Optional Tools
- **MongoDB Compass** - GUI for MongoDB
- **Redis Insight** - GUI for Redis
- **Postman** - API testing

---

## ⚡ Quick Start

### 1. Clone Repository
```bash
git clone <repository-url>
cd unilink-backend
```

### 2. Start Required Services

**MongoDB:**
```bash
mongod --dbpath /path/to/data
```

**Redis:**
```bash
redis-server
```

### 3. Configure Environment Variables

Create `.env` files in each service directory:

**app/.env**
```env
MONGO_URL=mongodb://localhost:27017/unilink
JWT_SECRET=your-secret-key-change-this
JWT_ALGORITHM=HS256
REDIS_HOST=localhost
REDIS_PORT=6379
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_S3_BUCKET_NAME=your-bucket
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
GEMINI_API_KEY=your-gemini-key
DISCORD_CLIENT_ID=your-discord-id
DISCORD_CLIENT_SECRET=your-discord-secret
DISCORD_REDIRECT_URI=http://localhost:3001/auth/discord/callback
CLIENT_URL=http://localhost:3000
SESSION_SECRET=your-session-secret
```

**chat-service/.env**
```env
MONGO_URL=mongodb://localhost:27017/chatdb
REDIS_HOST=localhost
REDIS_PORT=6379
JWT_SECRET=your-secret-key-change-this
MAIN_APP_URL=http://localhost:3000
```

**notification-service/.env**
```env
SERVER_PORT=8080
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=notifications
REDIS_HOST=localhost
REDIS_PORT=6379
JWT_SECRET=your-secret-key-change-this
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### 4. Start All Services

**Linux/macOS:**
```bash
chmod +x start-all.sh
./start-all.sh
```

**Windows:**
```cmd
start-all.bat
```

**Manual Start:**

```bash
# Terminal 1 - Main API
cd app
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r ../requirements.txt
uvicorn main:app --host 0.0.0.0 --port 3001

# Terminal 2 - Chat Service
cd chat-service
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn main:app --host 0.0.0.0 --port 4000

# Terminal 3 - Notification Service
cd notification-service
go mod download
go build -o notification-service cmd/server/main.go
./notification-service
```

### 5. Verify Services

```bash
curl http://localhost:3001/       # Main API
curl http://localhost:4000/health # Chat Service
curl http://localhost:8080/health # Notification Service
```

---

## 🔧 Configuration

### Main API Endpoints
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/discord` - Discord OAuth
- `GET /users/:id` - Get user profile
- `POST /posts` - Create post
- `GET /posts` - Get feed
- `POST /s3/upload-url/profile` - Get S3 upload URL
- `POST /captions/generate` - Generate AI captions
- `POST /otp/send` - Send OTP
- `POST /otp/verify` - Verify OTP

### Chat Service Endpoints
- `GET /api/chat/conversations` - Get conversations
- `GET /api/chat/conversations/:id/messages` - Get messages
- `POST /api/chat/messages` - Send message
- `GET /api/chat/users/search` - Search users
- **WebSocket:** `ws://localhost:4000/socket.io`

### Notification Service Endpoints
- `GET /api/notifications` - Get notifications
- `GET /api/notifications/unread-count` - Get count
- `PATCH /api/notifications/:id/read` - Mark as read
- `GET /api/notifications/preferences` - Get preferences
- **WebSocket:** `ws://localhost:8080/ws`

---

## 📚 API Documentation

### Authentication

All protected endpoints require a JWT token in the Authorization header:

```http
Authorization: Bearer <your-jwt-token>
```

### Example: User Registration

```bash
curl -X POST http://localhost:3001/otp/send \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "password": "SecurePass123",
    "location": "New York",
    "Year": "2024"
  }'
```

## 🔨 Development

### Running Tests

**Main API:**
```bash
cd app
pytest
```

**Notification Service:**
```bash
cd notification-service
go test ./...
```

### Testing WebSockets

**Chat Service:**
```bash
# Use the test client at http://localhost:4000/test.html
```

**Notification Service:**
```bash
# Open notification-service/scripts/test.html in browser
```

### Testing Notifications

```bash
cd notification-service/scripts
python3 test_notifications.py
```

---

## 🐛 Troubleshooting

#### Go Build Error
```
Error: cannot use result.InsertedID
```
**Solution:** Replace the notification model file with the fixed version provided

#### WebSocket Connection Failed
**Solution:** 
- Check JWT token is valid
- Ensure service is running
- Check browser console for errors

### Logs

View service logs:
```bash
# Linux/macOS
tail -f logs/main.log
tail -f logs/chat.log
tail -f logs/notification.log

# Windows
type logs\main.log
```

---

## 📝 Environment Variables Reference

### Main API
| Variable | Description | Example |
|----------|-------------|---------|
| `MONGO_URL` | MongoDB connection string | `mongodb://localhost:27017/unilink` |
| `JWT_SECRET` | Secret key for JWT | `your-secret-key` |
| `AWS_S3_BUCKET_NAME` | S3 bucket name | `unilink-uploads` |
| `GEMINI_API_KEY` | Google Gemini API key | `AIza...` |

### Chat Service
| Variable | Description | Example |
|----------|-------------|---------|
| `MONGO_URL` | MongoDB connection string | `mongodb://localhost:27017/chatdb` |
| `REDIS_HOST` | Redis host | `localhost` |
| `JWT_SECRET` | Must match main API | `your-secret-key` |

### Notification Service
| Variable | Description | Example |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017` |
| `REDIS_HOST` | Redis host | `localhost` |
| `JWT_SECRET` | Must match main API | `your-secret-key` |


**Built with ❤️ for university students**

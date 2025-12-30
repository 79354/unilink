notification-service/
├── cmd/
│   └── server/
│       └── main.go
├── internal/
│   ├── config/
│   │   └── config.go
│   ├── database/
│   │   └── database.go          # Only this file (no migrations.go)
│   ├── handler/
│   │   ├── notification.go
│   │   ├── preferences.go
│   │   └── websocket.go
│   ├── middleware/
│   │   └── auth.go
│   ├── model/
│   │   ├── notification.go
│   │   └── preferences.go
│   └── service/
│       ├── event_listener.go
│       ├── notification.go
│       ├── preferences.go
│       ├── queue.go
│       └── websocket.go
├── scripts/
│   ├── test.html
│   ├── test_api.sh
│   └── test_notifications.py
├── .env
├── go.mod
└── go.sum
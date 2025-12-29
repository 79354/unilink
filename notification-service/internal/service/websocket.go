package service

import (
	"context"
	"encoding/json"
	"sync"
	"time"

	"github.com/gorilla/websocket"
	"github.com/redis/go-redis/v9"
	"go.uber.org/zap"
)

const (
	onlineUsersKey = "notification:online"
	socketPrefix   = "notification:socket:"
	writeWait      = 10 * time.Second
	pongWait       = 60 * time.Second
	pingPeriod     = (pongWait * 9) / 10
)

type WebSocketService interface {
	RegisterClient(userID string, conn *websocket.Conn)
	UnregisterClient(userID string)
	SendToUser(userID string, event string, payload interface{})
	SendUnreadCount(userID string, count int64)
	IsUserOnline(userID string) bool
}

type wsMessage struct {
	Event   string      `json:"event"`
	Payload interface{} `json:"payload"`
}

type webSocketService struct {
	clients map[string]*websocket.Conn
	mu      sync.RWMutex
	redis   *redis.Client
	logger  *zap.Logger
}

func NewWebSocketService(
	redis *redis.Client,
	logger *zap.Logger,
) WebSocketService {
	return &webSocketService{
		clients: make(map[string]*websocket.Conn),
		redis:   redis,
		logger:  logger,
	}
}

func (s *webSocketService) RegisterClient(userID string, conn *websocket.Conn) {
	s.mu.Lock()
	s.clients[userID] = conn
	s.mu.Unlock()

	ctx := context.Background()
	s.redis.SAdd(ctx, onlineUsersKey, userID)
	s.redis.Set(ctx, socketPrefix+userID, "connected", 24*time.Hour)

	s.logger.Info("User connected", zap.String("userId", userID))

	// Start ping/pong
	go s.writePump(userID, conn)
}

func (s *webSocketService) UnregisterClient(userID string) {
	s.mu.Lock()
	if conn, exists := s.clients[userID]; exists {
		conn.Close()
		delete(s.clients, userID)
	}
	s.mu.Unlock()

	ctx := context.Background()
	s.redis.SRem(ctx, onlineUsersKey, userID)
	s.redis.Del(ctx, socketPrefix+userID)

	s.logger.Info("User disconnected", zap.String("userId", userID))
}

func (s *webSocketService) SendToUser(userID string, event string, payload interface{}) {
	s.mu.RLock()
	conn, exists := s.clients[userID]
	s.mu.RUnlock()

	if !exists {
		s.logger.Info("User offline, notification stored in DB", zap.String("userId", userID))
		return
	}

	msg := wsMessage{
		Event:   event,
		Payload: payload,
	}

	data, err := json.Marshal(msg)
	if err != nil {
		s.logger.Error("Failed to marshal message", zap.Error(err))
		return
	}

	conn.SetWriteDeadline(time.Now().Add(writeWait))
	if err := conn.WriteMessage(websocket.TextMessage, data); err != nil {
		s.logger.Error("Failed to send message", zap.Error(err))
		s.UnregisterClient(userID)
		return
	}

	s.logger.Info("Sent message",
		zap.String("userId", userID),
		zap.String("event", event),
	)
}

func (s *webSocketService) SendUnreadCount(userID string, count int64) {
	s.SendToUser(userID, "notification:unread-count", map[string]interface{}{
		"count": count,
	})
}

func (s *webSocketService) IsUserOnline(userID string) bool {
	ctx := context.Background()
	isMember, err := s.redis.SIsMember(ctx, onlineUsersKey, userID).Result()
	return err == nil && isMember
}

func (s *webSocketService) writePump(userID string, conn *websocket.Conn) {
	ticker := time.NewTicker(pingPeriod)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			conn.SetWriteDeadline(time.Now().Add(writeWait))
			if err := conn.WriteMessage(websocket.PingMessage, nil); err != nil {
				s.UnregisterClient(userID)
				return
			}
		}
	}
}
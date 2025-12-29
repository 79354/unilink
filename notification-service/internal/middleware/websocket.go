package handler

import (
	"net/http"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"github.com/gorilla/websocket"
	"go.uber.org/zap"

	"github.com/unilink/notification-service/internal/service"
)

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin: func(r *http.Request) bool {
		return true // Configure appropriately for production
	},
}

type WebSocketHandler struct {
	websocketService    service.WebSocketService
	notificationService service.NotificationService
	jwtSecret           string
	logger              *zap.Logger
}

func NewWebSocketHandler(
	websocketService service.WebSocketService,
	notificationService service.NotificationService,
	jwtSecret string,
	logger *zap.Logger,
) *WebSocketHandler {
	return &WebSocketHandler{
		websocketService:    websocketService,
		notificationService: notificationService,
		jwtSecret:           jwtSecret,
		logger:              logger,
	}
}

func (h *WebSocketHandler) HandleWebSocket(c *gin.Context) {
	// Extract JWT token from query parameter or header
	tokenString := c.Query("token")
	if tokenString == "" {
		authHeader := c.GetHeader("Authorization")
		if authHeader != "" {
			parts := strings.Split(authHeader, " ")
			if len(parts) == 2 && parts[0] == "Bearer" {
				tokenString = parts[1]
			}
		}
	}

	if tokenString == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Token required"})
		return
	}

	// Validate JWT token
	token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, jwt.ErrSignatureInvalid
		}
		return []byte(h.jwtSecret), nil
	})

	if err != nil || !token.Valid {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid or expired token"})
		return
	}

	// Extract user ID
	claims, ok := token.Claims.(jwt.MapClaims)
	if !ok {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid token claims"})
		return
	}

	userID, ok := claims["id"].(string)
	if !ok || userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "User ID not found in token"})
		return
	}

	// Upgrade to WebSocket
	conn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
	if err != nil {
		h.logger.Error("Failed to upgrade to WebSocket", zap.Error(err))
		return
	}

	// Register client
	h.websocketService.RegisterClient(userID, conn)
	defer h.websocketService.UnregisterClient(userID)

	// Send initial unread count
	count, _ := h.notificationService.GetUnreadCount(userID)
	h.websocketService.SendUnreadCount(userID, count)

	h.logger.Info("✅ WebSocket connected", zap.String("userId", userID))

	// Read pump - handle incoming messages
	h.readPump(conn, userID)
}

func (h *WebSocketHandler) readPump(conn *websocket.Conn, userID string) {
	defer conn.Close()

	conn.SetReadDeadline(time.Now().Add(60 * time.Second))
	conn.SetPongHandler(func(string) error {
		conn.SetReadDeadline(time.Now().Add(60 * time.Second))
		return nil
	})

	for {
		messageType, message, err := conn.ReadMessage()
		if err != nil {
			if websocket.IsUnexpectedCloseError(err, websocket.CloseGoingAway, websocket.CloseAbnormalClosure) {
				h.logger.Error("WebSocket error", zap.Error(err))
			}
			break
		}

		if messageType == websocket.TextMessage {
			h.logger.Debug("Received message", zap.String("userId", userID), zap.String("message", string(message)))
			// Handle incoming messages if needed (e.g., mark as read, etc.)
		}
	}

	h.logger.Info("❌ WebSocket disconnected", zap.String("userId", userID))
}
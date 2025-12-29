package service

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/redis/go-redis/v9"
	"go.uber.org/zap"

	"github.com/unilink/notification-service/internal/config"
	"github.com/unilink/notification-service/internal/model"
)

type EventListener struct {
	redis        *redis.Client
	queueService *QueueService
	config       *config.Config
	logger       *zap.Logger
}

func NewEventListener(
	redis *redis.Client,
	queueService *QueueService,
	cfg *config.Config,
	logger *zap.Logger,
) *EventListener {
	return &EventListener{
		redis:        redis,
		queueService: queueService,
		config:       cfg,
		logger:       logger,
	}
}

func (l *EventListener) Start(ctx context.Context) {
	l.logger.Info("🎧 Starting Redis Pub/Sub event listener...")

	// Subscribe to all notification channels
	channels := l.config.GetAllChannels()
	pubsub := l.redis.Subscribe(ctx, channels...)
	defer pubsub.Close()

	l.logger.Info("✅ Event listener started",
		zap.Int("channels", len(channels)),
		zap.Strings("subscribed", channels),
	)

	// Listen for messages
	ch := pubsub.Channel()
	for {
		select {
		case <-ctx.Done():
			l.logger.Info("Event listener shutting down...")
			return

		case msg := <-ch:
			l.handleMessage(ctx, msg)
		}
	}
}

func (l *EventListener) handleMessage(ctx context.Context, msg *redis.Message) {
	l.logger.Info("📨 Received event",
		zap.String("channel", msg.Channel),
		zap.String("payload", msg.Payload),
	)

	// Parse event data
	var eventData model.NotificationEvent
	if err := json.Unmarshal([]byte(msg.Payload), &eventData); err != nil {
		l.logger.Error("❌ Failed to parse event data", zap.Error(err))
		return
	}

	// Validate required fields
	if eventData.UserID == "" || eventData.ActorID == "" || eventData.ActorName == "" {
		l.logger.Error("❌ Invalid notification data: missing required fields")
		return
	}

	// Determine notification type from channel
	notificationType := l.config.GetChannelType(msg.Channel)
	if notificationType == "" {
		l.logger.Warn("⚠️ Unknown channel", zap.String("channel", msg.Channel))
		return
	}

	eventData.Type = notificationType

	// Generate message if not provided
	if eventData.Message == "" {
		eventData.Message = l.generateMessage(&eventData)
	}

	// Queue for processing
	if err := l.queueService.Enqueue(ctx, &eventData); err != nil {
		l.logger.Error("❌ Failed to queue notification", zap.Error(err))
	}
}

func (l *EventListener) generateMessage(data *model.NotificationEvent) string {
	switch data.Type {
	case "like":
		return fmt.Sprintf("%s liked your post", data.ActorName)
	case "message":
		return fmt.Sprintf("%s sent you a message", data.ActorName)
	case "profile-view":
		return fmt.Sprintf("%s viewed your profile", data.ActorName)
	case "friend-post":
		return fmt.Sprintf("%s shared a new post", data.ActorName)
	case "friend-request":
		return fmt.Sprintf("%s sent you a friend request", data.ActorName)
	default:
		return "New notification"
	}
}
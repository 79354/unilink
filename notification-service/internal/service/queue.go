package service

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"github.com/redis/go-redis/v9"
	"go.uber.org/zap"

	"github.com/unilink/notification-service/internal/config"
	"github.com/unilink/notification-service/internal/model"
)

const (
	queueStreamKey = "notifications:queue"
	consumerGroup  = "notification-processors"
)

type PriorityConfig struct {
	Priority int
	Delay    time.Duration
}

var priorityMap = map[string]PriorityConfig{
	"message":        {Priority: 1, Delay: 0},
	"friend-request": {Priority: 2, Delay: 0},
	"like":           {Priority: 3, Delay: 2 * time.Second},
	"profile-view":   {Priority: 4, Delay: 3 * time.Second},
	"friend-post":    {Priority: 5, Delay: 5 * time.Second},
}

type QueueService struct {
	redis               *redis.Client
	notificationService NotificationService
	websocketService    WebSocketService
	config              *config.Config
	logger              *zap.Logger
}

func NewQueueService(
	redis *redis.Client,
	notificationService NotificationService,
	websocketService WebSocketService,
	cfg *config.Config,
	logger *zap.Logger,
) *QueueService {
	return &QueueService{
		redis:               redis,
		notificationService: notificationService,
		websocketService:    websocketService,
		config:              cfg,
		logger:              logger,
	}
}

func (s *QueueService) Start(ctx context.Context) {
	s.logger.Info("Starting notification queue processors...")

	s.initConsumerGroup(ctx)

	for i := 0; i < s.config.NotificationQueueWorkers; i++ {
		go s.processQueue(ctx, fmt.Sprintf("worker-%d", i))
	}

	s.logger.Info("Queue processors started",
		zap.Int("workers", s.config.NotificationQueueWorkers),
	)
}

func (s *QueueService) initConsumerGroup(ctx context.Context) {
	err := s.redis.XGroupCreateMkStream(ctx, queueStreamKey, consumerGroup, "0").Err()
	if err != nil && err.Error() != "BUSYGROUP Consumer Group name already exists" {
		s.logger.Error("Failed to create consumer group", zap.Error(err))
	}
}

func (s *QueueService) Enqueue(ctx context.Context, event *model.NotificationEvent) error {
	priorityConfig := priorityMap[event.Type]
	if priorityConfig.Delay > 0 {
		time.Sleep(priorityConfig.Delay)
	}

	data, err := json.Marshal(event)
	if err != nil {
		return err
	}

	_, err = s.redis.XAdd(ctx, &redis.XAddArgs{
		Stream: queueStreamKey,
		Values: map[string]interface{}{
			"data": string(data),
		},
	}).Result()

	if err != nil {
		return err
	}

	s.logger.Info("Queued notification",
		zap.String("type", event.Type),
		zap.String("userId", event.UserID),
	)

	return nil
}

func (s *QueueService) processQueue(ctx context.Context, consumerName string) {
	for {
		select {
		case <-ctx.Done():
			s.logger.Info("Queue processor shutting down", zap.String("consumer", consumerName))
			return
		default:
			s.readAndProcess(ctx, consumerName)
		}
	}
}

func (s *QueueService) readAndProcess(ctx context.Context, consumerName string) {
	streams, err := s.redis.XReadGroup(ctx, &redis.XReadGroupArgs{
		Group:    consumerGroup,
		Consumer: consumerName,
		Streams:  []string{queueStreamKey, ">"},
		Count:    1,
		Block:    5 * time.Second,
	}).Result()

	if err != nil {
		if err != redis.Nil {
			s.logger.Error("Failed to read from stream", zap.Error(err))
		}
		return
	}

	for _, stream := range streams {
		for _, message := range stream.Messages {
			s.processMessage(ctx, message, consumerName)
		}
	}
}

func (s *QueueService) processMessage(ctx context.Context, message redis.XMessage, consumerName string) {
	defer func() {
		s.redis.XAck(ctx, queueStreamKey, consumerGroup, message.ID)
	}()

	dataStr, ok := message.Values["data"].(string)
	if !ok {
		s.logger.Error("Invalid message format")
		return
	}

	var event model.NotificationEvent
	if err := json.Unmarshal([]byte(dataStr), &event); err != nil {
		s.logger.Error("Failed to unmarshal event", zap.Error(err))
		return
	}

	s.logger.Info("Processing notification",
		zap.String("type", event.Type),
		zap.String("userId", event.UserID),
		zap.String("consumer", consumerName),
	)

	if event.Type == "like" || event.Type == "profile-view" {
		if existingID := s.checkDeduplication(ctx, &event); existingID != "" {
			s.handleGroupedNotification(ctx, existingID, &event)
			return
		}
	}

	var relatedID *string
	if event.RelatedID != "" {
		relatedID = &event.RelatedID
	}

	notification := &model.Notification{
		UserID:       event.UserID,
		Type:         model.NotificationType(event.Type),
		ActorID:      event.ActorID,
		ActorName:    event.ActorName,
		ActorPicture: event.ActorPicture,
		RelatedID:    relatedID,
		Message:      event.Message,
		Priority:     s.getPriority(event.Priority),
		Metadata:     event.Metadata,
		Read:         false,
	}

	if notification.Metadata == nil {
		notification.Metadata = make(map[string]interface{})
	}
	notification.Metadata["groupCount"] = 1

	createdNotification, err := s.notificationService.CreateNotification(notification)
	if err != nil {
		s.logger.Error("Failed to create notification", zap.Error(err))
		return
	}

	if event.Type == "like" || event.Type == "profile-view" {
		dedupKey := s.getDeduplicationKey(&event)
		s.redis.Set(ctx, dedupKey, createdNotification.ID.Hex(), time.Duration(s.config.NotificationGroupingWindowSecs)*time.Second)
	}

	s.websocketService.SendToUser(event.UserID, "notification:new", createdNotification)

	count, _ := s.notificationService.GetUnreadCount(event.UserID)
	s.websocketService.SendUnreadCount(event.UserID, count)

	s.logger.Info("Notification processed", zap.String("id", createdNotification.ID.Hex()))
}

func (s *QueueService) handleGroupedNotification(ctx context.Context, notificationID string, event *model.NotificationEvent) {
	notification, err := s.notificationService.FindByID(notificationID)
	if err != nil || notification == nil {
		return
	}

	currentCount := notification.GetGroupCount()
	notification.Metadata["groupCount"] = float64(currentCount + 1)

	if currentCount == 1 {
		notification.Message = fmt.Sprintf(
			"%s and 1 other %s your %s",
			event.ActorName,
			s.getActionVerb(event.Type),
			s.getTargetNoun(event.Type),
		)
	} else {
		notification.Message = fmt.Sprintf(
			"%s and %d others %s your %s",
			event.ActorName,
			currentCount,
			s.getActionVerb(event.Type),
			s.getTargetNoun(event.Type),
		)
	}

	s.notificationService.UpdateNotification(notification)
	s.websocketService.SendToUser(event.UserID, "notification:updated", notification)

	s.logger.Info("Grouped notification updated",
		zap.String("id", notificationID),
		zap.Int("count", currentCount+1),
	)
}

func (s *QueueService) checkDeduplication(ctx context.Context, event *model.NotificationEvent) string {
	dedupKey := s.getDeduplicationKey(event)
	id, err := s.redis.Get(ctx, dedupKey).Result()
	if err == redis.Nil {
		return ""
	}
	return id
}

func (s *QueueService) getDeduplicationKey(event *model.NotificationEvent) string {
	relatedID := event.RelatedID
	if relatedID == "" {
		relatedID = "none"
	}
	return fmt.Sprintf("notification:dedup:%s:%s:%s:%s",
		event.Type, event.UserID, event.ActorID, relatedID)
}

func (s *QueueService) getPriority(priority string) model.Priority {
	switch priority {
	case "high":
		return model.PriorityHigh
	case "low":
		return model.PriorityLow
	default:
		return model.PriorityMedium
	}
}

func (s *QueueService) getActionVerb(notifType string) string {
	switch notifType {
	case "like":
		return "liked"
	case "profile-view":
		return "viewed"
	default:
		return "interacted with"
	}
}

func (s *QueueService) getTargetNoun(notifType string) string {
	switch notifType {
	case "like":
		return "post"
	case "profile-view":
		return "profile"
	default:
		return "content"
	}
}
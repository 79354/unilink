package service

import (
	"time"

	"go.uber.org/zap"

	"github.com/unilink/notification-service/internal/model"
	"github.com/unilink/notification-service/internal/repository"
)

type NotificationService interface {
	GetNotifications(userID string, limit, offset int, unreadOnly bool) ([]*model.Notification, int64, error)
	GetUnreadCount(userID string) (int64, error)
	MarkAsRead(userID, notificationID string) (*model.Notification, error)
	MarkAllAsRead(userID string) error
	DeleteNotification(userID, notificationID string) error
	DeleteAllNotifications(userID string) error
	CreateNotification(notification *model.Notification) (*model.Notification, error)
	UpdateNotification(notification *model.Notification) (*model.Notification, error)
	FindByID(notificationID string) (*model.Notification, error)
	GetStatistics(userID string) ([]*model.NotificationStatistics, error)
}

type notificationService struct {
	repo   repository.NotificationRepository
	logger *zap.Logger
}

func NewNotificationService(
	repo repository.NotificationRepository,
	logger *zap.Logger,
) NotificationService {
	return &notificationService{
		repo:   repo,
		logger: logger,
	}
}

func (s *notificationService) GetNotifications(userID string, limit, offset int, unreadOnly bool) ([]*model.Notification, int64, error) {
	return s.repo.FindByUserID(userID, limit, offset, unreadOnly)
}

func (s *notificationService) GetUnreadCount(userID string) (int64, error) {
	return s.repo.CountUnread(userID)
}

func (s *notificationService) MarkAsRead(userID, notificationID string) (*model.Notification, error) {
	if err := s.repo.MarkAsRead(userID, notificationID); err != nil {
		return nil, err
	}
	return s.repo.FindByID(notificationID)
}

func (s *notificationService) MarkAllAsRead(userID string) error {
	err := s.repo.MarkAllAsRead(userID)
	if err == nil {
		s.logger.Info("Marked all notifications as read", zap.String("userId", userID))
	}
	return err
}

func (s *notificationService) DeleteNotification(userID, notificationID string) error {
	return s.repo.Delete(userID, notificationID)
}

func (s *notificationService) DeleteAllNotifications(userID string) error {
	err := s.repo.DeleteAllByUserID(userID)
	if err == nil {
		s.logger.Info("Deleted all notifications", zap.String("userId", userID))
	}
	return err
}

func (s *notificationService) CreateNotification(notification *model.Notification) (*model.Notification, error) {
	// Set default expiration if not provided
	if notification.ExpiresAt == nil {
		expiresAt := time.Now().AddDate(0, 0, 90) // 90 days
		notification.ExpiresAt = &expiresAt
	}

	if err := s.repo.Create(notification); err != nil {
		return nil, err
	}

	s.logger.Info("Notification created",
		zap.String("id", notification.ID),
		zap.String("type", string(notification.Type)),
		zap.String("userId", notification.UserID),
	)

	return notification, nil
}

func (s *notificationService) UpdateNotification(notification *model.Notification) (*model.Notification, error) {
	if err := s.repo.Update(notification); err != nil {
		return nil, err
	}
	return notification, nil
}

func (s *notificationService) FindByID(notificationID string) (*model.Notification, error) {
	return s.repo.FindByID(notificationID)
}

func (s *notificationService) GetStatistics(userID string) ([]*model.NotificationStatistics, error) {
	return s.repo.GetStatistics(userID)
}
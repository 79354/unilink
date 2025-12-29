package service

import (
	"go.uber.org/zap"

	"github.com/unilink/notification-service/internal/model"
	"github.com/unilink/notification-service/internal/repository"
)

type PreferencesService interface {
	GetOrCreate(userID string) (*model.UserPreferences, error)
	UpdatePreferences(userID string, updates *model.UserPreferences) (*model.UserPreferences, error)
	IsNotificationEnabled(userID, notificationType string) (bool, error)
	IsInQuietHours(userID string) (bool, error)
}

type preferencesService struct {
	repo   repository.PreferencesRepository
	logger *zap.Logger
}

func NewPreferencesService(
	repo repository.PreferencesRepository,
	logger *zap.Logger,
) PreferencesService {
	return &preferencesService{
		repo:   repo,
		logger: logger,
	}
}

func (s *preferencesService) GetOrCreate(userID string) (*model.UserPreferences, error) {
	preferences, err := s.repo.FindByUserID(userID)
	if err != nil {
		return nil, err
	}

	if preferences == nil {
		s.logger.Info("Creating default preferences", zap.String("userId", userID))
		preferences = model.NewDefaultPreferences(userID)
		if err := s.repo.Create(preferences); err != nil {
			return nil, err
		}
	}

	return preferences, nil
}

func (s *preferencesService) UpdatePreferences(userID string, updates *model.UserPreferences) (*model.UserPreferences, error) {
	existing, err := s.GetOrCreate(userID)
	if err != nil {
		return nil, err
	}

	// Update fields if provided
	if updates.Notifications != nil && len(updates.Notifications) > 0 {
		existing.Notifications = updates.Notifications
	}

	if updates.EmailNotifications != existing.EmailNotifications {
		existing.EmailNotifications = updates.EmailNotifications
	}

	if updates.PushNotifications != existing.PushNotifications {
		existing.PushNotifications = updates.PushNotifications
	}

	if updates.QuietHours.Enabled != existing.QuietHours.Enabled ||
		updates.QuietHours.Start != existing.QuietHours.Start ||
		updates.QuietHours.End != existing.QuietHours.End {
		existing.QuietHours = updates.QuietHours
	}

	if err := s.repo.Update(existing); err != nil {
		return nil, err
	}

	s.logger.Info("Preferences updated", zap.String("userId", userID))

	return existing, nil
}

func (s *preferencesService) IsNotificationEnabled(userID, notificationType string) (bool, error) {
	preferences, err := s.GetOrCreate(userID)
	if err != nil {
		return false, err
	}
	return preferences.IsEnabled(notificationType), nil
}

func (s *preferencesService) IsInQuietHours(userID string) (bool, error) {
	preferences, err := s.GetOrCreate(userID)
	if err != nil {
		return false, err
	}
	return preferences.IsInQuietHours(), nil
}
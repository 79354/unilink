package service

import (
	"context"
	"time"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"go.uber.org/zap"

	"github.com/unilink/notification-service/internal/model"
)

type PreferencesService interface {
	GetOrCreate(userID string) (*model.UserPreferences, error)
	UpdatePreferences(userID string, updates *model.UserPreferences) (*model.UserPreferences, error)
	IsNotificationEnabled(userID, notificationType string) (bool, error)
	IsInQuietHours(userID string) (bool, error)
}

type preferencesService struct {
	collection *mongo.Collection
	logger     *zap.Logger
}

func NewPreferencesService(db *mongo.Database, logger *zap.Logger) PreferencesService {
	return &preferencesService{
		collection: db.Collection("user_preferences"),
		logger:     logger,
	}
}

func (s *preferencesService) GetOrCreate(userID string) (*model.UserPreferences, error) {
	ctx := context.Background()

	var preferences model.UserPreferences
	err := s.collection.FindOne(ctx, bson.M{"userId": userID}).Decode(&preferences)

	if err == mongo.ErrNoDocuments {
		s.logger.Info("Creating default preferences", zap.String("userId", userID))
		preferences := model.NewDefaultPreferences(userID)

		_, err := s.collection.InsertOne(ctx, preferences)
		if err != nil {
			return nil, err
		}

		return preferences, nil
	}

	if err != nil {
		return nil, err
	}

	return &preferences, nil
}

func (s *preferencesService) UpdatePreferences(userID string, updates *model.UserPreferences) (*model.UserPreferences, error) {
	ctx := context.Background()

	existing, err := s.GetOrCreate(userID)
	if err != nil {
		return nil, err
	}

	if updates.Notifications != nil && len(updates.Notifications) > 0 {
		existing.Notifications = updates.Notifications
	}

	existing.EmailNotifications = updates.EmailNotifications
	existing.PushNotifications = updates.PushNotifications

	if updates.QuietHours.Start != "" {
		existing.QuietHours = updates.QuietHours
	}

	existing.UpdatedAt = time.Now()

	filter := bson.M{"userId": userID}
	update := bson.M{
		"$set": bson.M{
			"notifications":      existing.Notifications,
			"emailNotifications": existing.EmailNotifications,
			"pushNotifications":  existing.PushNotifications,
			"quietHours":         existing.QuietHours,
			"updatedAt":          existing.UpdatedAt,
		},
	}

	err = s.collection.FindOneAndUpdate(
		ctx,
		filter,
		update,
		options.FindOneAndUpdate().SetReturnDocument(options.After),
	).Decode(existing)

	if err == nil {
		s.logger.Info("Preferences updated", zap.String("userId", userID))
	}

	return existing, err
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
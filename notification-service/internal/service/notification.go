package service

import (
	"context"
	"time"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"go.uber.org/zap"

	"github.com/unilink/notification-service/internal/model"
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
	collection *mongo.Collection
	logger     *zap.Logger
}

func NewNotificationService(db *mongo.Database, logger *zap.Logger) NotificationService {
	return &notificationService{
		collection: db.Collection("notifications"),
		logger:     logger,
	}
}

func (s *notificationService) GetNotifications(userID string, limit, offset int, unreadOnly bool) ([]*model.Notification, int64, error) {
	ctx := context.Background()

	filter := bson.M{"userId": userID}
	if unreadOnly {
		filter["read"] = false
	}

	total, err := s.collection.CountDocuments(ctx, filter)
	if err != nil {
		return nil, 0, err
	}

	opts := options.Find().
		SetSort(bson.D{{Key: "createdAt", Value: -1}}).
		SetLimit(int64(limit)).
		SetSkip(int64(offset))

	cursor, err := s.collection.Find(ctx, filter, opts)
	if err != nil {
		return nil, 0, err
	}
	defer cursor.Close(ctx)

	var notifications []*model.Notification
	if err := cursor.All(ctx, &notifications); err != nil {
		return nil, 0, err
	}

	return notifications, total, nil
}

func (s *notificationService) GetUnreadCount(userID string) (int64, error) {
	ctx := context.Background()
	filter := bson.M{"userId": userID, "read": false}
	return s.collection.CountDocuments(ctx, filter)
}

func (s *notificationService) MarkAsRead(userID, notificationID string) (*model.Notification, error) {
	ctx := context.Background()

	objID, err := primitive.ObjectIDFromHex(notificationID)
	if err != nil {
		return nil, err
	}

	filter := bson.M{"_id": objID, "userId": userID}
	update := bson.M{
		"$set": bson.M{
			"read":      true,
			"updatedAt": time.Now(),
		},
	}

	var notification model.Notification
	err = s.collection.FindOneAndUpdate(
		ctx,
		filter,
		update,
		options.FindOneAndUpdate().SetReturnDocument(options.After),
	).Decode(&notification)

	if err != nil {
		return nil, err
	}

	return &notification, nil
}

func (s *notificationService) MarkAllAsRead(userID string) error {
	ctx := context.Background()

	filter := bson.M{"userId": userID, "read": false}
	update := bson.M{
		"$set": bson.M{
			"read":      true,
			"updatedAt": time.Now(),
		},
	}

	_, err := s.collection.UpdateMany(ctx, filter, update)
	if err == nil {
		s.logger.Info("Marked all notifications as read", zap.String("userId", userID))
	}
	return err
}

func (s *notificationService) DeleteNotification(userID, notificationID string) error {
	ctx := context.Background()

	objID, err := primitive.ObjectIDFromHex(notificationID)
	if err != nil {
		return err
	}

	filter := bson.M{"_id": objID, "userId": userID}
	result, err := s.collection.DeleteOne(ctx, filter)
	if err != nil {
		return err
	}

	if result.DeletedCount == 0 {
		return mongo.ErrNoDocuments
	}

	return nil
}

func (s *notificationService) DeleteAllNotifications(userID string) error {
	ctx := context.Background()
	filter := bson.M{"userId": userID}

	_, err := s.collection.DeleteMany(ctx, filter)
	if err == nil {
		s.logger.Info("Deleted all notifications", zap.String("userId", userID))
	}
	return err
}

func (s *notificationService) CreateNotification(notification *model.Notification) (*model.Notification, error) {
	ctx := context.Background()

	if notification.ExpiresAt == nil {
		expiresAt := time.Now().AddDate(0, 0, 90)
		notification.ExpiresAt = &expiresAt
	}

	notification.CreatedAt = time.Now()
	notification.UpdatedAt = time.Now()

	result, err := s.collection.InsertOne(ctx, notification)
	if err != nil {
		return nil, err
	}

	notification.ID = result.InsertedID.(primitive.ObjectID)

	s.logger.Info("Notification created",
		zap.String("id", notification.ID.Hex()),
		zap.String("type", string(notification.Type)),
		zap.String("userId", notification.UserID),
	)

	return notification, nil
}

func (s *notificationService) UpdateNotification(notification *model.Notification) (*model.Notification, error) {
	ctx := context.Background()

	notification.UpdatedAt = time.Now()

	filter := bson.M{"_id": notification.ID}
	update := bson.M{
		"$set": bson.M{
			"message":   notification.Message,
			"read":      notification.Read,
			"metadata":  notification.Metadata,
			"updatedAt": notification.UpdatedAt,
		},
	}

	err := s.collection.FindOneAndUpdate(
		ctx,
		filter,
		update,
		options.FindOneAndUpdate().SetReturnDocument(options.After),
	).Decode(notification)

	return notification, err
}

func (s *notificationService) FindByID(notificationID string) (*model.Notification, error) {
	ctx := context.Background()

	objID, err := primitive.ObjectIDFromHex(notificationID)
	if err != nil {
		return nil, err
	}

	var notification model.Notification
	err = s.collection.FindOne(ctx, bson.M{"_id": objID}).Decode(&notification)
	if err != nil {
		return nil, err
	}

	return &notification, nil
}

func (s *notificationService) GetStatistics(userID string) ([]*model.NotificationStatistics, error) {
	ctx := context.Background()

	pipeline := []bson.M{
		{"$match": bson.M{"userId": userID}},
		{
			"$group": bson.M{
				"_id":   "$type",
				"count": bson.M{"$sum": 1},
				"unread": bson.M{
					"$sum": bson.M{
						"$cond": []interface{}{
							bson.M{"$eq": []interface{}{"$read", false}},
							1,
							0,
						},
					},
				},
			},
		},
	}

	cursor, err := s.collection.Aggregate(ctx, pipeline)
	if err != nil {
		return nil, err
	}
	defer cursor.Close(ctx)

	var stats []*model.NotificationStatistics
	if err := cursor.All(ctx, &stats); err != nil {
		return nil, err
	}

	return stats, nil
}
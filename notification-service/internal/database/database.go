package database

import (
	"context"
	"fmt"
	"time"

	"github.com/redis/go-redis/v9"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"

	"github.com/unilink/notification-service/internal/config"
)

func NewMongoDB(cfg *config.Config) (*mongo.Database, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	clientOptions := options.Client().ApplyURI(cfg.MongoDBURI)
	client, err := mongo.Connect(ctx, clientOptions)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to MongoDB: %w", err)
	}

	if err := client.Ping(ctx, nil); err != nil {
		return nil, fmt.Errorf("failed to ping MongoDB: %w", err)
	}

	db := client.Database(cfg.MongoDBDatabase)

	if err := createIndexes(ctx, db); err != nil {
		return nil, fmt.Errorf("failed to create indexes: %w", err)
	}

	return db, nil
}

func createIndexes(ctx context.Context, db *mongo.Database) error {
	notificationsCol := db.Collection("notifications")

	indexes := []mongo.IndexModel{
		{
			Keys: map[string]interface{}{"userId": 1},
		},
		{
			Keys: map[string]interface{}{"userId": 1, "createdAt": -1},
		},
		{
			Keys: map[string]interface{}{"userId": 1, "read": 1},
		},
		{
			Keys: map[string]interface{}{"expiresAt": 1},
			Options: options.Index().SetExpireAfterSeconds(0),
		},
	}

	_, err := notificationsCol.Indexes().CreateMany(ctx, indexes)
	if err != nil {
		return err
	}

	preferencesCol := db.Collection("user_preferences")
	_, err = preferencesCol.Indexes().CreateOne(ctx, mongo.IndexModel{
		Keys:    map[string]interface{}{"userId": 1},
		Options: options.Index().SetUnique(true),
	})

	return err
}

func NewRedisClient(cfg *config.Config) *redis.Client {
	client := redis.NewClient(&redis.Options{
		Addr:     fmt.Sprintf("%s:%d", cfg.RedisHost, cfg.RedisPort),
		Password: cfg.RedisPassword,
		DB:       0,
	})

	ctx := context.Background()
	if err := client.Ping(ctx).Err(); err != nil {
		panic(fmt.Sprintf("Failed to connect to Redis: %v", err))
	}

	return client
}
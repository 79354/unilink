package config

import (
	"os"
	"strconv"

	"github.com/joho/godotenv"
)

type Config struct {
	ServerPort int
	ServerMode string

	MongoDBURI      string
	MongoDBDatabase string

	RedisHost     string
	RedisPort     int
	RedisPassword string

	JWTSecret string

	CORSAllowedOrigins string

	NotificationQueueWorkers       int
	NotificationGroupingWindowSecs int
	NotificationDefaultExpiryDays  int
}

var notificationChannels = map[string]string{
	"notification:like":           "like",
	"notification:message":        "message",
	"notification:profile-view":   "profile-view",
	"notification:friend-post":    "friend-post",
	"notification:friend-request": "friend-request",
}

func Load() (*Config, error) {
	godotenv.Load()

	cfg := &Config{
		ServerPort: getEnvAsInt("SERVER_PORT", 8080),
		ServerMode: getEnv("SERVER_MODE", "development"),

		MongoDBURI:      getEnv("MONGODB_URI", "mongodb://localhost:27017"),
		MongoDBDatabase: getEnv("MONGODB_DATABASE", "notifications"),

		RedisHost:     getEnv("REDIS_HOST", "localhost"),
		RedisPort:     getEnvAsInt("REDIS_PORT", 6379),
		RedisPassword: getEnv("REDIS_PASSWORD", ""),

		JWTSecret: getEnv("JWT_SECRET", "your-secret-key"),

		CORSAllowedOrigins: getEnv("CORS_ALLOWED_ORIGINS", "http://localhost:3000"),

		NotificationQueueWorkers:       getEnvAsInt("NOTIFICATION_QUEUE_WORKERS", 3),
		NotificationGroupingWindowSecs: getEnvAsInt("NOTIFICATION_GROUPING_WINDOW_SECS", 300),
		NotificationDefaultExpiryDays:  getEnvAsInt("NOTIFICATION_DEFAULT_EXPIRY_DAYS", 90),
	}

	return cfg, nil
}

func (c *Config) GetAllChannels() []string {
	channels := make([]string, 0, len(notificationChannels))
	for channel := range notificationChannels {
		channels = append(channels, channel)
	}
	return channels
}

func (c *Config) GetChannelType(channel string) string {
	return notificationChannels[channel]
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getEnvAsInt(key string, defaultValue int) int {
	valueStr := os.Getenv(key)
	if valueStr == "" {
		return defaultValue
	}
	value, err := strconv.Atoi(valueStr)
	if err != nil {
		return defaultValue
	}
	return value
}
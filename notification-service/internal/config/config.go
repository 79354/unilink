package config

import (
	"fmt"
	"os"
	"strconv"

	"github.com/joho/godotenv"
)

type Config struct {
	// Server
	ServerPort int
	ServerMode string

	// Database
	DBHost     string
	DBPort     int
	DBUser     string
	DBPassword string
	DBName     string

	// Redis
	RedisHost     string
	RedisPort     int
	RedisPassword string

	// JWT
	JWTSecret string

	// CORS
	CORSAllowedOrigins string

	// Notification settings
	NotificationQueueWorkers        int
	NotificationGroupingWindowSecs  int
	NotificationDefaultExpiryDays   int
}

var notificationChannels = map[string]string{
	"notification:like":           "like",
	"notification:message":        "message",
	"notification:profile-view":   "profile-view",
	"notification:friend-post":    "friend-post",
	"notification:friend-request": "friend-request",
}

func Load() (*Config, error) {
	// Load .env file if exists
	godotenv.Load()

	cfg := &Config{
		ServerPort: getEnvAsInt("SERVER_PORT", 8080),
		ServerMode: getEnv("SERVER_MODE", "development"),

		DBHost:     getEnv("DB_HOST", "localhost"),
		DBPort:     getEnvAsInt("DB_PORT", 5432),
		DBUser:     getEnv("DB_USER", "postgres"),
		DBPassword: getEnv("DB_PASSWORD", ""),
		DBName:     getEnv("DB_NAME", "notifications"),

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
		fmt.Printf("Warning: Invalid value for %s, using default %d\n", key, defaultValue)
		return defaultValue
	}
	return value
}
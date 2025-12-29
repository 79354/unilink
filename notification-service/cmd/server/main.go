package main

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"go.uber.org/zap"

	"github.com/unilink/notification-service/internal/config"
	"github.com/unilink/notification-service/internal/database"
	"github.com/unilink/notification-service/internal/handler"
	"github.com/unilink/notification-service/internal/middleware"
	"github.com/unilink/notification-service/internal/repository"
	"github.com/unilink/notification-service/internal/service"
)

func main() {
	// Initialize logger
	logger, _ := zap.NewProduction()
	defer logger.Sync()

	// Load configuration
	cfg, err := config.Load()
	if err != nil {
		logger.Fatal("Failed to load config", zap.Error(err))
	}

	// Initialize databases
	db, err := database.NewPostgresDB(cfg)
	if err != nil {
		logger.Fatal("Failed to connect to PostgreSQL", zap.Error(err))
	}
	defer db.Close()

	// Run migrations
	if err := database.RunMigrations(db); err != nil {
		logger.Fatal("Failed to run migrations", zap.Error(err))
	}

	redisClient := database.NewRedisClient(cfg)
	defer redisClient.Close()

	// Initialize repositories
	notificationRepo := repository.NewNotificationRepository(db)
	preferencesRepo := repository.NewPreferencesRepository(db)

	// Initialize services
	notificationService := service.NewNotificationService(notificationRepo, logger)
	preferencesService := service.NewPreferencesService(preferencesRepo, logger)
	websocketService := service.NewWebSocketService(redisClient, logger)
	queueService := service.NewQueueService(
		redisClient,
		notificationService,
		websocketService,
		cfg,
		logger,
	)
	eventListener := service.NewEventListener(
		redisClient,
		queueService,
		cfg,
		logger,
	)

	// Initialize handlers
	notificationHandler := handler.NewNotificationHandler(notificationService, logger)
	preferencesHandler := handler.NewPreferencesHandler(preferencesService, logger)
	websocketHandler := handler.NewWebSocketHandler(
		websocketService,
		notificationService,
		cfg.JWTSecret,
		logger,
	)

	// Setup Gin router
	if cfg.ServerMode == "production" {
		gin.SetMode(gin.ReleaseMode)
	}

	router := gin.Default()

	// CORS configuration
	router.Use(cors.New(cors.Config{
		AllowOrigins:     []string{cfg.CORSAllowedOrigins},
		AllowMethods:     []string{"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Authorization"},
		AllowCredentials: true,
		MaxAge:           12 * time.Hour,
	}))

	// Health check
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "healthy"})
	})

	// WebSocket endpoint (no auth middleware)
	router.GET("/ws", websocketHandler.HandleWebSocket)

	// API routes with JWT authentication
	api := router.Group("/api")
	api.Use(middleware.JWTAuth(cfg.JWTSecret))
	{
		notifications := api.Group("/notifications")
		{
			notifications.GET("", notificationHandler.GetNotifications)
			notifications.GET("/unread-count", notificationHandler.GetUnreadCount)
			notifications.PATCH("/:id/read", notificationHandler.MarkAsRead)
			notifications.PATCH("/read-all", notificationHandler.MarkAllAsRead)
			notifications.DELETE("/:id", notificationHandler.DeleteNotification)
			notifications.DELETE("/all", notificationHandler.DeleteAllNotifications)
			notifications.GET("/statistics", notificationHandler.GetStatistics)

			// Preferences
			notifications.GET("/preferences", preferencesHandler.GetPreferences)
			notifications.PATCH("/preferences", preferencesHandler.UpdatePreferences)
		}
	}

	// Start background services
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	go queueService.Start(ctx)
	go eventListener.Start(ctx)

	// Start server
	srv := &http.Server{
		Addr:    fmt.Sprintf(":%d", cfg.ServerPort),
		Handler: router,
	}

	go func() {
		logger.Info("Server starting",
			zap.Int("port", cfg.ServerPort),
			zap.String("mode", cfg.ServerMode),
		)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Fatal("Failed to start server", zap.Error(err))
		}
	}()

	// Graceful shutdown
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	logger.Info("Shutting down server...")

	shutdownCtx, shutdownCancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer shutdownCancel()

	if err := srv.Shutdown(shutdownCtx); err != nil {
		logger.Fatal("Server forced to shutdown", zap.Error(err))
	}

	logger.Info("Server stopped gracefully")
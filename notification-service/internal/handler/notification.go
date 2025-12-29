package handler

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"

	"github.com/unilink/notification-service/internal/middleware"
	"github.com/unilink/notification-service/internal/service"
)

type NotificationHandler struct {
	notificationService service.NotificationService
	logger              *zap.Logger
}

func NewNotificationHandler(
	notificationService service.NotificationService,
	logger *zap.Logger,
) *NotificationHandler {
	return &NotificationHandler{
		notificationService: notificationService,
		logger:              logger,
	}
}

func (h *NotificationHandler) GetNotifications(c *gin.Context) {
	userID := middleware.GetUserID(c)

	page, _ := strconv.Atoi(c.DefaultQuery("page", "0"))
	size, _ := strconv.Atoi(c.DefaultQuery("size", "20"))
	unreadOnlyStr := c.Query("unreadOnly")
	unreadOnly := unreadOnlyStr == "true"

	notifications, total, err := h.notificationService.GetNotifications(userID, size, page*size, unreadOnly)
	if err != nil {
		h.logger.Error("Failed to get notifications", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch notifications"})
		return
	}

	totalPages := (int(total) + size - 1) / size

	c.JSON(http.StatusOK, gin.H{
		"notifications":      notifications,
		"totalPages":         totalPages,
		"currentPage":        page,
		"totalNotifications": total,
	})
}

func (h *NotificationHandler) GetUnreadCount(c *gin.Context) {
	userID := middleware.GetUserID(c)

	count, err := h.notificationService.GetUnreadCount(userID)
	if err != nil {
		h.logger.Error("Failed to get unread count", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch count"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"count": count})
}

func (h *NotificationHandler) MarkAsRead(c *gin.Context) {
	userID := middleware.GetUserID(c)
	notificationID := c.Param("id")

	notification, err := h.notificationService.MarkAsRead(userID, notificationID)
	if err != nil {
		h.logger.Error("Failed to mark as read", zap.Error(err))
		c.JSON(http.StatusNotFound, gin.H{"error": "Notification not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message":      "Notification marked as read",
		"notification": notification,
	})
}

func (h *NotificationHandler) MarkAllAsRead(c *gin.Context) {
	userID := middleware.GetUserID(c)

	if err := h.notificationService.MarkAllAsRead(userID); err != nil {
		h.logger.Error("Failed to mark all as read", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update notifications"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "All notifications marked as read"})
}

func (h *NotificationHandler) DeleteNotification(c *gin.Context) {
	userID := middleware.GetUserID(c)
	notificationID := c.Param("id")

	if err := h.notificationService.DeleteNotification(userID, notificationID); err != nil {
		h.logger.Error("Failed to delete notification", zap.Error(err))
		c.JSON(http.StatusNotFound, gin.H{"error": "Notification not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Notification deleted"})
}

func (h *NotificationHandler) DeleteAllNotifications(c *gin.Context) {
	userID := middleware.GetUserID(c)

	if err := h.notificationService.DeleteAllNotifications(userID); err != nil {
		h.logger.Error("Failed to delete all notifications", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete notifications"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "All notifications deleted"})
}

func (h *NotificationHandler) GetStatistics(c *gin.Context) {
	userID := middleware.GetUserID(c)

	stats, err := h.notificationService.GetStatistics(userID)
	if err != nil {
		h.logger.Error("Failed to get statistics", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch statistics"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"statistics": stats})
}
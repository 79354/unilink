package handler

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"

	"github.com/unilink/notification-service/internal/middleware"
	"github.com/unilink/notification-service/internal/model"
	"github.com/unilink/notification-service/internal/service"
)

type PreferencesHandler struct {
	preferencesService service.PreferencesService
	logger             *zap.Logger
}

func NewPreferencesHandler(
	preferencesService service.PreferencesService,
	logger *zap.Logger,
) *PreferencesHandler {
	return &PreferencesHandler{
		preferencesService: preferencesService,
		logger:             logger,
	}
}

func (h *PreferencesHandler) GetPreferences(c *gin.Context) {
	userID := middleware.GetUserID(c)

	preferences, err := h.preferencesService.GetOrCreate(userID)
	if err != nil {
		h.logger.Error("Failed to get preferences", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch preferences"})
		return
	}

	c.JSON(http.StatusOK, preferences)
}

func (h *PreferencesHandler) UpdatePreferences(c *gin.Context) {
	userID := middleware.GetUserID(c)

	var updates model.UserPreferences
	if err := c.ShouldBindJSON(&updates); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request body"})
		return
	}

	preferences, err := h.preferencesService.UpdatePreferences(userID, &updates)
	if err != nil {
		h.logger.Error("Failed to update preferences", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update preferences"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message":     "Preferences updated",
		"preferences": preferences,
	})
}
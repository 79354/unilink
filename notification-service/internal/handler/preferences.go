package model

import (
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

type QuietHours struct {
	Enabled bool   `bson:"enabled" json:"enabled"`
	Start   string `bson:"start" json:"start"`
	End     string `bson:"end" json:"end"`
}

type UserPreferences struct {
	ID                 primitive.ObjectID `bson:"_id,omitempty" json:"id"`
	UserID             string             `bson:"userId" json:"userId"`
	Notifications      map[string]bool    `bson:"notifications" json:"notifications"`
	EmailNotifications bool               `bson:"emailNotifications" json:"emailNotifications"`
	PushNotifications  bool               `bson:"pushNotifications" json:"pushNotifications"`
	QuietHours         QuietHours         `bson:"quietHours" json:"quietHours"`
	CreatedAt          time.Time          `bson:"createdAt" json:"createdAt"`
	UpdatedAt          time.Time          `bson:"updatedAt" json:"updatedAt"`
}

func (p *UserPreferences) IsEnabled(notificationType string) bool {
	if p.Notifications == nil {
		return true
	}
	enabled, exists := p.Notifications[notificationType]
	if !exists {
		return true
	}
	return enabled
}

func (p *UserPreferences) IsInQuietHours() bool {
	if !p.QuietHours.Enabled {
		return false
	}

	now := time.Now()
	currentTime := now.Format("15:04")

	start := p.QuietHours.Start
	end := p.QuietHours.End

	if start > end {
		return currentTime >= start || currentTime < end
	}
	return currentTime >= start && currentTime < end
}

func NewDefaultPreferences(userID string) *UserPreferences {
	return &UserPreferences{
		UserID: userID,
		Notifications: map[string]bool{
			"like":           true,
			"message":        true,
			"profile-view":   true,
			"friend-post":    true,
			"friend-request": true,
		},
		EmailNotifications: true,
		PushNotifications:  true,
		QuietHours: QuietHours{
			Enabled: false,
			Start:   "22:00",
			End:     "08:00",
		},
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
}
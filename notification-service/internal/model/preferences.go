package model

import (
	"database/sql/driver"
	"encoding/json"
	"time"
)

type NotificationPreferences map[string]bool

func (np NotificationPreferences) Value() (driver.Value, error) {
	return json.Marshal(np)
}

func (np *NotificationPreferences) Scan(value interface{}) error {
	if value == nil {
		*np = make(NotificationPreferences)
		return nil
	}
	bytes, ok := value.([]byte)
	if !ok {
		return nil
	}
	return json.Unmarshal(bytes, np)
}

type QuietHours struct {
	Enabled bool   `json:"enabled"`
	Start   string `json:"start"`
	End     string `json:"end"`
}

func (qh QuietHours) Value() (driver.Value, error) {
	return json.Marshal(qh)
}

func (qh *QuietHours) Scan(value interface{}) error {
	if value == nil {
		*qh = QuietHours{
			Enabled: false,
			Start:   "22:00",
			End:     "08:00",
		}
		return nil
	}
	bytes, ok := value.([]byte)
	if !ok {
		return nil
	}
	return json.Unmarshal(bytes, qh)
}

type UserPreferences struct {
	ID                   string                  `db:"id" json:"id"`
	UserID               string                  `db:"user_id" json:"userId"`
	Notifications        NotificationPreferences `db:"notifications" json:"notifications"`
	EmailNotifications   bool                    `db:"email_notifications" json:"emailNotifications"`
	PushNotifications    bool                    `db:"push_notifications" json:"pushNotifications"`
	QuietHours           QuietHours              `db:"quiet_hours" json:"quietHours"`
	CreatedAt            time.Time               `db:"created_at" json:"createdAt"`
	UpdatedAt            time.Time               `db:"updated_at" json:"updatedAt"`
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
		// Quiet hours span midnight
		return currentTime >= start || currentTime < end
	}
	return currentTime >= start && currentTime < end
}

func NewDefaultPreferences(userID string) *UserPreferences {
	return &UserPreferences{
		UserID: userID,
		Notifications: NotificationPreferences{
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
	}
}
package model

import (
	"database/sql/driver"
	"encoding/json"
	"time"
)

type NotificationType string

const (
	NotificationTypeLike          NotificationType = "like"
	NotificationTypeMessage       NotificationType = "message"
	NotificationTypeProfileView   NotificationType = "profile-view"
	NotificationTypeFriendPost    NotificationType = "friend-post"
	NotificationTypeFriendRequest NotificationType = "friend-request"
)

type Priority string

const (
	PriorityHigh   Priority = "HIGH"
	PriorityMedium Priority = "MEDIUM"
	PriorityLow    Priority = "LOW"
)

type Metadata map[string]interface{}

func (m Metadata) Value() (driver.Value, error) {
	return json.Marshal(m)
}

func (m *Metadata) Scan(value interface{}) error {
	if value == nil {
		*m = make(Metadata)
		return nil
	}
	bytes, ok := value.([]byte)
	if !ok {
		return nil
	}
	return json.Unmarshal(bytes, m)
}

type Notification struct {
	ID           string           `db:"id" json:"id"`
	UserID       string           `db:"user_id" json:"userId"`
	Type         NotificationType `db:"type" json:"type"`
	ActorID      string           `db:"actor_id" json:"actorId"`
	ActorName    string           `db:"actor_name" json:"actorName"`
	ActorPicture string           `db:"actor_picture" json:"actorPicture"`
	RelatedID    *string          `db:"related_id" json:"relatedId,omitempty"`
	Message      string           `db:"message" json:"message"`
	Read         bool             `db:"read" json:"read"`
	Priority     Priority         `db:"priority" json:"priority"`
	Metadata     Metadata         `db:"metadata" json:"metadata"`
	ExpiresAt    *time.Time       `db:"expires_at" json:"expiresAt,omitempty"`
	CreatedAt    time.Time        `db:"created_at" json:"createdAt"`
	UpdatedAt    time.Time        `db:"updated_at" json:"updatedAt"`
}

func (n *Notification) IsGrouped() bool {
	if n.Metadata == nil {
		return false
	}
	count, ok := n.Metadata["groupCount"]
	if !ok {
		return false
	}
	countFloat, ok := count.(float64)
	return ok && countFloat > 1
}

func (n *Notification) GetGroupCount() int {
	if n.Metadata == nil {
		return 1
	}
	count, ok := n.Metadata["groupCount"]
	if !ok {
		return 1
	}
	switch v := count.(type) {
	case float64:
		return int(v)
	case int:
		return v
	default:
		return 1
	}
}

type NotificationEvent struct {
	UserID       string                 `json:"userId"`
	Type         string                 `json:"type"`
	ActorID      string                 `json:"actorId"`
	ActorName    string                 `json:"actorName"`
	ActorPicture string                 `json:"actorPicture"`
	RelatedID    string                 `json:"relatedId"`
	Message      string                 `json:"message"`
	Priority     string                 `json:"priority"`
	Metadata     map[string]interface{} `json:"metadata"`
}

type NotificationStatistics struct {
	Type   string `db:"type" json:"type"`
	Count  int64  `db:"count" json:"count"`
	Unread int64  `db:"unread" json:"unread"`
}
package model

import (
	"database/sql/driver"
	"encoding/json"
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
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
	ID           primitive.ObjectID `bson:"_id,omitempty" json:"id"`
	UserID       string             `bson:"userId" json:"userId"`
	Type         NotificationType   `bson:"type" json:"type"`
	ActorID      string             `bson:"actorId" json:"actorId"`
	ActorName    string             `bson:"actorName" json:"actorName"`
	ActorPicture string             `bson:"actorPicture" json:"actorPicture"`
	RelatedID    *string            `bson:"relatedId,omitempty" json:"relatedId,omitempty"`
	Message      string             `bson:"message" json:"message"`
	Read         bool               `bson:"read" json:"read"`
	Priority     Priority           `bson:"priority" json:"priority"`
	Metadata     Metadata           `bson:"metadata" json:"metadata"`
	ExpiresAt    *time.Time         `bson:"expiresAt,omitempty" json:"expiresAt,omitempty"`
	CreatedAt    time.Time          `bson:"createdAt" json:"createdAt"`
	UpdatedAt    time.Time          `bson:"updatedAt" json:"updatedAt"`
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
	Type   string `bson:"_id" json:"type"`
	Count  int64  `bson:"count" json:"count"`
	Unread int64  `bson:"unread" json:"unread"`
}
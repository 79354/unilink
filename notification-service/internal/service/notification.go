package repository

import (
	"database/sql"
	"fmt"
	"time"

	"github.com/jmoiron/sqlx"

	"github.com/unilink/notification-service/internal/model"
)

type NotificationRepository interface {
	Create(notification *model.Notification) error
	FindByID(id string) (*model.Notification, error)
	FindByUserID(userID string, limit, offset int, unreadOnly bool) ([]*model.Notification, int64, error)
	Update(notification *model.Notification) error
	MarkAsRead(userID, notificationID string) error
	MarkAllAsRead(userID string) error
	Delete(userID, notificationID string) error
	DeleteAllByUserID(userID string) error
	CountUnread(userID string) (int64, error)
	GetStatistics(userID string) ([]*model.NotificationStatistics, error)
}

type notificationRepository struct {
	db *sqlx.DB
}

func NewNotificationRepository(db *sqlx.DB) NotificationRepository {
	return &notificationRepository{db: db}
}

func (r *notificationRepository) Create(notification *model.Notification) error {
	query := `
		INSERT INTO notifications (
			user_id, type, actor_id, actor_name, actor_picture,
			related_id, message, read, priority, metadata, expires_at
		) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
		RETURNING id, created_at, updated_at
	`

	return r.db.QueryRowx(
		query,
		notification.UserID,
		notification.Type,
		notification.ActorID,
		notification.ActorName,
		notification.ActorPicture,
		notification.RelatedID,
		notification.Message,
		notification.Read,
		notification.Priority,
		notification.Metadata,
		notification.ExpiresAt,
	).Scan(&notification.ID, &notification.CreatedAt, &notification.UpdatedAt)
}

func (r *notificationRepository) FindByID(id string) (*model.Notification, error) {
	var notification model.Notification
	query := `SELECT * FROM notifications WHERE id = $1`

	err := r.db.Get(&notification, query, id)
	if err == sql.ErrNoRows {
		return nil, nil
	}

	return &notification, err
}

func (r *notificationRepository) FindByUserID(userID string, limit, offset int, unreadOnly bool) ([]*model.Notification, int64, error) {
	var notifications []*model.Notification
	var total int64

	// Build query based on unreadOnly flag
	query := `SELECT * FROM notifications WHERE user_id = $1`
	countQuery := `SELECT COUNT(*) FROM notifications WHERE user_id = $1`

	if unreadOnly {
		query += ` AND read = FALSE`
		countQuery += ` AND read = FALSE`
	}

	query += ` ORDER BY created_at DESC LIMIT $2 OFFSET $3`

	// Get total count
	if err := r.db.Get(&total, countQuery, userID); err != nil {
		return nil, 0, err
	}

	// Get notifications
	if err := r.db.Select(&notifications, query, userID, limit, offset); err != nil {
		return nil, 0, err
	}

	return notifications, total, nil
}

func (r *notificationRepository) Update(notification *model.Notification) error {
	query := `
		UPDATE notifications
		SET message = $1, read = $2, metadata = $3, updated_at = CURRENT_TIMESTAMP
		WHERE id = $4
		RETURNING updated_at
	`

	return r.db.QueryRow(
		query,
		notification.Message,
		notification.Read,
		notification.Metadata,
		notification.ID,
	).Scan(&notification.UpdatedAt)
}

func (r *notificationRepository) MarkAsRead(userID, notificationID string) error {
	query := `
		UPDATE notifications
		SET read = TRUE, updated_at = CURRENT_TIMESTAMP
		WHERE id = $1 AND user_id = $2
	`

	result, err := r.db.Exec(query, notificationID, userID)
	if err != nil {
		return err
	}

	rows, err := result.RowsAffected()
	if err != nil {
		return err
	}

	if rows == 0 {
		return fmt.Errorf("notification not found or unauthorized")
	}

	return nil
}

func (r *notificationRepository) MarkAllAsRead(userID string) error {
	query := `
		UPDATE notifications
		SET read = TRUE, updated_at = CURRENT_TIMESTAMP
		WHERE user_id = $1 AND read = FALSE
	`

	_, err := r.db.Exec(query, userID)
	return err
}

func (r *notificationRepository) Delete(userID, notificationID string) error {
	query := `DELETE FROM notifications WHERE id = $1 AND user_id = $2`

	result, err := r.db.Exec(query, notificationID, userID)
	if err != nil {
		return err
	}

	rows, err := result.RowsAffected()
	if err != nil {
		return err
	}

	if rows == 0 {
		return fmt.Errorf("notification not found or unauthorized")
	}

	return nil
}

func (r *notificationRepository) DeleteAllByUserID(userID string) error {
	query := `DELETE FROM notifications WHERE user_id = $1`
	_, err := r.db.Exec(query, userID)
	return err
}

func (r *notificationRepository) CountUnread(userID string) (int64, error) {
	var count int64
	query := `SELECT COUNT(*) FROM notifications WHERE user_id = $1 AND read = FALSE`

	err := r.db.Get(&count, query, userID)
	return count, err
}

func (r *notificationRepository) GetStatistics(userID string) ([]*model.NotificationStatistics, error) {
	var stats []*model.NotificationStatistics

	query := `
		SELECT
			type,
			COUNT(*) as count,
			SUM(CASE WHEN read = FALSE THEN 1 ELSE 0 END) as unread
		FROM notifications
		WHERE user_id = $1
		GROUP BY type
	`

	err := r.db.Select(&stats, query, userID)
	return stats, err
}
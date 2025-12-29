package repository

import (
	"database/sql"

	"github.com/jmoiron/sqlx"

	"github.com/unilink/notification-service/internal/model"
)

type PreferencesRepository interface {
	Create(preferences *model.UserPreferences) error
	FindByUserID(userID string) (*model.UserPreferences, error)
	Update(preferences *model.UserPreferences) error
}

type preferencesRepository struct {
	db *sqlx.DB
}

func NewPreferencesRepository(db *sqlx.DB) PreferencesRepository {
	return &preferencesRepository{db: db}
}

func (r *preferencesRepository) Create(preferences *model.UserPreferences) error {
	query := `
		INSERT INTO user_preferences (
			user_id, notifications, email_notifications,
			push_notifications, quiet_hours
		) VALUES ($1, $2, $3, $4, $5)
		RETURNING id, created_at, updated_at
	`

	return r.db.QueryRowx(
		query,
		preferences.UserID,
		preferences.Notifications,
		preferences.EmailNotifications,
		preferences.PushNotifications,
		preferences.QuietHours,
	).Scan(&preferences.ID, &preferences.CreatedAt, &preferences.UpdatedAt)
}

func (r *preferencesRepository) FindByUserID(userID string) (*model.UserPreferences, error) {
	var preferences model.UserPreferences
	query := `SELECT * FROM user_preferences WHERE user_id = $1`

	err := r.db.Get(&preferences, query, userID)
	if err == sql.ErrNoRows {
		return nil, nil
	}

	return &preferences, err
}

func (r *preferencesRepository) Update(preferences *model.UserPreferences) error {
	query := `
		UPDATE user_preferences
		SET notifications = $1,
		    email_notifications = $2,
		    push_notifications = $3,
		    quiet_hours = $4,
		    updated_at = CURRENT_TIMESTAMP
		WHERE user_id = $5
		RETURNING updated_at
	`

	return r.db.QueryRow(
		query,
		preferences.Notifications,
		preferences.EmailNotifications,
		preferences.PushNotifications,
		preferences.QuietHours,
		preferences.UserID,
	).Scan(&preferences.UpdatedAt)
}
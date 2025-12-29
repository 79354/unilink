package database

import (
	"github.com/jmoiron/sqlx"
)

func RunMigrations(db *sqlx.DB) error {
	migrations := []string{
		// Enable UUID extension
		`CREATE EXTENSION IF NOT EXISTS "uuid-ossp";`,

		// Create notifications table
		`CREATE TABLE IF NOT EXISTS notifications (
			id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
			user_id VARCHAR(255) NOT NULL,
			type VARCHAR(50) NOT NULL,
			actor_id VARCHAR(255) NOT NULL,
			actor_name VARCHAR(255) NOT NULL,
			actor_picture TEXT,
			related_id VARCHAR(255),
			message TEXT NOT NULL,
			read BOOLEAN DEFAULT FALSE,
			priority VARCHAR(20) DEFAULT 'MEDIUM',
			metadata JSONB DEFAULT '{}'::jsonb,
			expires_at TIMESTAMP,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		);`,

		// Create indexes for notifications
		`CREATE INDEX IF NOT EXISTS idx_notifications_user_id 
			ON notifications(user_id);`,

		`CREATE INDEX IF NOT EXISTS idx_notifications_user_id_created_at 
			ON notifications(user_id, created_at DESC);`,

		`CREATE INDEX IF NOT EXISTS idx_notifications_user_id_read 
			ON notifications(user_id, read);`,

		`CREATE INDEX IF NOT EXISTS idx_notifications_expires_at 
			ON notifications(expires_at);`,

		// Create user_preferences table
		`CREATE TABLE IF NOT EXISTS user_preferences (
			id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
			user_id VARCHAR(255) UNIQUE NOT NULL,
			notifications JSONB DEFAULT '{"like": true, "message": true, "profile-view": true, "friend-request": true, "friend-post": true}'::jsonb,
			email_notifications BOOLEAN DEFAULT TRUE,
			push_notifications BOOLEAN DEFAULT TRUE,
			quiet_hours JSONB DEFAULT '{"enabled": false, "start": "22:00", "end": "08:00"}'::jsonb,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		);`,

		// Create index for user_preferences
		`CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id 
			ON user_preferences(user_id);`,

		// Create trigger to update updated_at timestamp
		`CREATE OR REPLACE FUNCTION update_updated_at_column()
		RETURNS TRIGGER AS $$
		BEGIN
			NEW.updated_at = CURRENT_TIMESTAMP;
			RETURN NEW;
		END;
		$$ LANGUAGE plpgsql;`,

		`DROP TRIGGER IF EXISTS update_notifications_updated_at ON notifications;`,
		`CREATE TRIGGER update_notifications_updated_at
			BEFORE UPDATE ON notifications
			FOR EACH ROW
			EXECUTE FUNCTION update_updated_at_column();`,

		`DROP TRIGGER IF EXISTS update_user_preferences_updated_at ON user_preferences;`,
		`CREATE TRIGGER update_user_preferences_updated_at
			BEFORE UPDATE ON user_preferences
			FOR EACH ROW
			EXECUTE FUNCTION update_updated_at_column();`,
	}

	for _, migration := range migrations {
		if _, err := db.Exec(migration); err != nil {
			return err
		}
	}

	return nil
}
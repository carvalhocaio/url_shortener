-- Migration: Add created_at column to urls table
-- Date: 2025-10-27
-- Description: Adds timestamp tracking for URL creation (Issue #2 - Peek URL)

-- Add created_at column with default value for existing records
ALTER TABLE urls
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- Update existing records to use current timestamp
-- (New records will use datetime.utcnow from SQLAlchemy)
UPDATE urls
SET created_at = CURRENT_TIMESTAMP
WHERE created_at IS NULL;

-- Migration: 002_add_task_completed
-- Created: 2025-07-09
-- Description: Add completed column to tasks table

-- Up migration
ALTER TABLE tasks ADD COLUMN completed BOOLEAN DEFAULT FALSE;

-- Down migration (rollback)
-- ALTER TABLE tasks DROP COLUMN completed;
-- Migration script to add user_id columns to todos and tasks tables

-- Add user_id column to todos table
ALTER TABLE todos 
ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1,
ADD FOREIGN KEY (user_id) REFERENCES users(id);

-- Add user_id column to tasks table  
ALTER TABLE tasks
ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1,
ADD FOREIGN KEY (user_id) REFERENCES users(id);

-- Remove unique constraint on base_date from todos table (if exists)
-- ALTER TABLE todos DROP INDEX base_date;

-- Note: The default value of 1 assumes there's at least one user with id=1
-- You may need to adjust this based on your actual user data
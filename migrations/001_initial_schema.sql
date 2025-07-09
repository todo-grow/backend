-- Migration: 001_initial_schema
-- Created: 2025-07-09
-- Description: Initial database schema with todos and tasks tables

-- Up migration
CREATE TABLE todos (
    id INTEGER NOT NULL AUTO_INCREMENT,
    title VARCHAR(255),
    base_date DATE,
    PRIMARY KEY (id)
);

CREATE TABLE tasks (
    id INTEGER NOT NULL AUTO_INCREMENT,
    title VARCHAR(255),
    description VARCHAR(255),
    points INTEGER,
    todo_id INTEGER,
    PRIMARY KEY (id),
    FOREIGN KEY (todo_id) REFERENCES todos(id)
);

-- Down migration (rollback)
-- DROP TABLE tasks;
-- DROP TABLE todos;
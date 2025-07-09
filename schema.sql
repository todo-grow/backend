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
    completed BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (id),
    FOREIGN KEY (todo_id) REFERENCES todos(id)
);

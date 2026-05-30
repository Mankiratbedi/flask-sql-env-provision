-- SQLite Database Schema for Assets
CREATE TABLE assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL
    name TEXT NOT NULL,
    quantity INTEGER DEFAULT 0
);

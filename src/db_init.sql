CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    identifier TEXT UNIQUE,
    password TEXT
);

CREATE TABLE IF NOT EXISTS providers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    location TEXT,
    price INTEGER,
    capacity INTEGER,
    packages TEXT
);

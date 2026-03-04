DROP TABLE IF EXISTS tickets;

CREATE TABLE tickets (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT NOT NULL DEFAULT 'email',
  subject TEXT NOT NULL,
  body TEXT NOT NULL,
  category TEXT NOT NULL,
  priority TEXT NOT NULL,
  confidence REAL NOT NULL,
  routed_to TEXT NOT NULL,
  created_at TEXT NOT NULL
);
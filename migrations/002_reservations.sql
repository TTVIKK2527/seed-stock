CREATE TABLE reservations (
    id TEXT PRIMARY KEY NOT NULL,
    seed_id TEXT NOT NULL REFERENCES seeds(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    status TEXT NOT NULL CHECK (status IN ('active', 'cancelled')),
    created_at TEXT NOT NULL
);

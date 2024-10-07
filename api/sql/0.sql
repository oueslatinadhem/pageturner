-- SQLite

-- do not run this file
CREATE TABLE data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre VARCHAR(1024) NOT NULL,
    detail TEXT
);

INSERT INTO data (titre, detail) VALUES ("Exemple test", "Exemple de détail");


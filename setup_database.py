import sqlite3

# Connexion à la base de données
conn = sqlite3.connect("influencers.db")
cursor = conn.cursor()

# Création de la table influencers
cursor.execute('''
CREATE TABLE IF NOT EXISTS influencers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    followers_count INTEGER,
    avg_likes INTEGER,
    avg_comments INTEGER,
    engagement_rate REAL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Sauvegarde et fermeture
conn.commit()
conn.close()

print("✅ Base de données et table `influencers` créées avec succès !")
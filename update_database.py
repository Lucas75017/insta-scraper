import sqlite3

# Connexion à la base de données
conn = sqlite3.connect("influencers.db")
cursor = conn.cursor()

# Exemple d'ajout d'un influenceur (modifie les valeurs si besoin)
cursor.execute('''
INSERT INTO influencers (username, followers_count, avg_likes, avg_comments, engagement_rate)
VALUES (?, ?, ?, ?, ?)
''', ("test_influencer", 100000, 5000, 300, 5.3))

# Sauvegarde et fermeture
conn.commit()
conn.close()

print("✅ Données ajoutées avec succès !")
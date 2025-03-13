import os
import instaloader
import sqlite3
import datetime
import pandas as pd
import random
import time
from flask import Flask, jsonify, send_file

app = Flask(__name__)

# 📌 Définition du chemin des sessions
SESSION_DIR = "/root/.config/instaloader" if os.environ.get("RENDER") else os.path.expanduser("~/.config/instaloader")

# 📌 Vérification si les sessions existent
if not os.path.exists(SESSION_DIR):
    print("❌ Dossier des sessions introuvable.")
else:
    print(f"✅ Dossier des sessions trouvé : {SESSION_DIR}")

# 📌 Comptes Instagram disponibles
INSTAGRAM_ACCOUNTS = ["romeol62", "mart.inette92"]
CURRENT_ACCOUNT_INDEX = 0

def get_instagram_session():
    """Charge une session Instagram en alternant entre plusieurs comptes."""
    global CURRENT_ACCOUNT_INDEX
    L = instaloader.Instaloader()

    account = INSTAGRAM_ACCOUNTS[CURRENT_ACCOUNT_INDEX]
    CURRENT_ACCOUNT_INDEX = (CURRENT_ACCOUNT_INDEX + 1) % len(INSTAGRAM_ACCOUNTS)

    session_file = os.path.join(SESSION_DIR, f"session-{account}")

    if os.path.exists(session_file):
        try:
            L.load_session_from_file(account, filename=session_file)
            print(f"✅ Session chargée avec {account}")
            return L
        except Exception as e:
            print(f"❌ Erreur de connexion à {account} : {e}")
    else:
        print(f"❌ Session {session_file} introuvable.")
    
    return None

def scrape_instagram(username):
    """Scrape les statistiques d'un compte Instagram"""
    L = get_instagram_session()
    if not L:
        return jsonify({"error": "Impossible de se connecter à Instagram."})

    try:
        profile = instaloader.Profile.from_username(L.context, username)
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la récupération du profil : {e}"})

    print(f"📊 Récupération des données de {username}...")

    # 📌 Définition de la période de scraping (40 jours)
    forty_days_ago = datetime.datetime.now() - datetime.timedelta(days=40)

    posts_data = []
    for post in profile.get_posts():
        if post.date_utc > forty_days_ago:
            posts_data.append({
                'Date': post.date_utc,
                'Likes': post.likes,
                'Comments': post.comments,
                'Video Views': post.video_view_count if post.is_video else None,
                'URL': post.url
            })
            time.sleep(random.randint(30, 60))  # 📌 Pause pour éviter les blocages

    if not posts_data:
        return jsonify({"error": "Aucune publication trouvée pour les 40 derniers jours."})

    df = pd.DataFrame(posts_data)

    # 📌 Calcul des stats
    avg_likes = df['Likes'].mean()
    avg_comments = df['Comments'].mean()
    avg_video_views = df['Video Views'].mean() if df['Video Views'].notnull().any() else None
    followers_count = profile.followers
    engagement_rate = ((avg_likes + avg_comments) / followers_count) * 100 if followers_count else 0

    # 📌 Stocker dans SQLite
    save_influencer_data(username, followers_count, avg_likes, avg_comments, engagement_rate)

    # 📌 Générer un fichier Excel
    file_path = f"/tmp/{username}_stats.xlsx"
    with pd.ExcelWriter(file_path) as writer:
        df.to_excel(writer, index=False, sheet_name='Posts')

    return send_file(file_path, as_attachment=True)

def save_influencer_data(username, followers, avg_likes, avg_comments, engagement_rate):
    """Stocker les données en base SQLite"""
    conn = sqlite3.connect("influencers.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO influencers (name, followers_count, avg_likes, avg_comments, engagement_rate, last_updated)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (username, followers, avg_likes, avg_comments, engagement_rate))
    conn.commit()
    conn.close()

@app.route('/scrape/<username>')
def scrape(username):
    return scrape_instagram(username)

@app.route('/')
def home():
    return "<h1>Instagram Scraper</h1>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
import os
import random
import time
import datetime
import instaloader
import sqlite3
import pandas as pd
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

# 📂 **Forcer la création du dossier des sessions**
SESSION_DIR = ".config/instaloader"
if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)
    print(f"✅ Dossier des sessions créé : {SESSION_DIR}")
else:
    print(f"📂 Dossier des sessions déjà existant : {SESSION_DIR}")

# 🧑‍💻 **Comptes Instagram disponibles pour éviter le blocage**
INSTAGRAM_ACCOUNTS = ["mart.inette92", "romeol62"]
CURRENT_ACCOUNT_INDEX = 0  # Alterner entre les comptes

def get_instagram_session():
    """Charge une session Instagram en alternant entre plusieurs comptes."""
    global CURRENT_ACCOUNT_INDEX
    L = instaloader.Instaloader()

    if not INSTAGRAM_ACCOUNTS:
        return None

    account = INSTAGRAM_ACCOUNTS[CURRENT_ACCOUNT_INDEX]
    CURRENT_ACCOUNT_INDEX = (CURRENT_ACCOUNT_INDEX + 1) % len(INSTAGRAM_ACCOUNTS)  # Alterne les comptes

    session_file = os.path.join(SESSION_DIR, f"session-{account}")
    if not os.path.exists(session_file):
        print(f"❌ Session introuvable pour {account}")
        return None

    try:
        L.load_session_from_file(account, filename=session_file)
        print(f"✅ Session chargée avec {account}")
    except Exception as e:
        print(f"❌ Erreur de connexion avec {account} : {e}")
        return None

    return L

def wait_before_next_request():
    """Ajoute un délai aléatoire pour éviter les blocages d'Instagram."""
    delay = random.randint(30, 120)  # Entre 30 et 120 secondes
    print(f"⏳ Pause de {delay} secondes avant la prochaine requête...")
    time.sleep(delay)

def scrape_instagram(username):
    """Récupère les stats d'un compte Instagram et les stocke en base de données."""
    L = get_instagram_session()
    if not L:
        return {"error": "Impossible de se connecter à Instagram."}

    try:
        profile = instaloader.Profile.from_username(L.context, username)
    except Exception as e:
        return {"error": f"Erreur lors de la récupération du profil : {e}"}

    print(f"📊 Récupération des données de {username}...")

    # 📅 **Définition de la période de scraping**
    forty_days_ago = datetime.datetime.now() - datetime.timedelta(days=40)
    posts_data = []

    for post in profile.get_posts():
        if post.date_utc > forty_days_ago:
            video_views = post.video_view_count if post.is_video else None
            posts_data.append({
                'Date': post.date_utc,
                'Likes': post.likes,
                'Comments': post.comments,
                'Video Views': video_views,
                'URL': post.url
            })
            wait_before_next_request()

    if not posts_data:
        return {"error": "Aucune publication trouvée pour les 40 derniers jours."}

    # 📊 **Création du DataFrame**
    df = pd.DataFrame(posts_data)

    # 📈 **Calcul des statistiques**
    avg_likes = df['Likes'].mean()
    avg_comments = df['Comments'].mean()
    avg_video_views = df['Video Views'].mean() if df['Video Views'].notnull().any() else None
    avg_views = avg_video_views if avg_video_views is not None else avg_likes

    followers_count = profile.followers
    posts_count = len(df)
    engagement_rate = ((avg_likes + avg_comments) / followers_count) * 100 if followers_count else 0
    min_story_views = 0.1 * followers_count
    max_story_views = 0.2 * followers_count

    # 🎯 **Simulation des données démographiques**
    audience_demographics = {
        'Gender': {'Female': '60%', 'Male': '40%'},
        'Location': {'France': '50%', 'Belgique': '20%', 'Suisse': '10%', 'Autres': '20%'},
        'Age Distribution': {'18-24': '30%', '25-34': '50%', '35-44': '15%', '45+': '5%'}
    }

    # 🗂 **Stockage des données en base de données**
    save_influencer_data(username, followers_count, avg_likes, avg_comments, engagement_rate)

    # 📂 **Création du résumé**
    summary = {
        'Followers Count': followers_count,
        'Posts Count': posts_count,
        'Average Likes': avg_likes,
        'Average Comments': avg_comments,
        'Average Views': avg_views,
        'Engagement Rate (%)': engagement_rate,
        'Min Story Views': min_story_views,
        'Max Story Views': max_story_views,
        'Audience Demographics': str(audience_demographics)
    }

    # 📊 **Sauvegarde dans un fichier Excel**
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    file_path = os.path.join(desktop_path, f"{username}_stats.xlsx")

    with pd.ExcelWriter(file_path) as writer:
        df.to_excel(writer, index=False, sheet_name='Posts')
        summary_df = pd.DataFrame([summary])
        summary_df.to_excel(writer, index=False, sheet_name='Summary')

    return send_file(file_path, as_attachment=True)

def save_influencer_data(username, followers, avg_likes, avg_comments, engagement_rate):
    """Enregistre les données de l'influenceur dans SQLite."""
    conn = sqlite3.connect("influencers.db")
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO influencers (name, followers_count, avg_likes, avg_comments, engagement_rate, last_updated)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (username, followers, avg_likes, avg_comments, engagement_rate))

    conn.commit()
    conn.close()
    print(f"✅ Données de {username} enregistrées.")

@app.route('/scrape/<username>')
def scrape(username):
    """API permettant de scraper un influenceur via l'URL."""
    return scrape_instagram(username)

@app.route('/')
def home():
    """Page d'accueil web."""
    return '''
    <!doctype html>
    <html>
      <head>
        <title>Analyse Instagram</title>
      </head>
      <body>
        <h1>Analyse Instagram</h1>
        <form action="/scrape" method="get">
          Nom du profil: <input type="text" name="username" required>
          <input type="submit" value="Analyser">
        </form>
      </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=True)
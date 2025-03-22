from flask import Flask, jsonify, render_template
import instaloader
import os
import random
import time

app = Flask(__name__)

# 📌 Liste des comptes disponibles pour scraper
INSTAGRAM_ACCOUNTS = ["mart.inette92", "romeol62", "hubertmirgaton"]
CURRENT_ACCOUNT_INDEX = 0  # Index pour alterner les comptes

# 📌 Dossier des sessions
SESSION_FOLDER = "sessions"  # On utilise le bon dossier

def get_instagram_session():
    """ 📌 Charge une session Instagram en alternant entre plusieurs comptes """
    global CURRENT_ACCOUNT_INDEX
    L = instaloader.Instaloader()

    account = INSTAGRAM_ACCOUNTS[CURRENT_ACCOUNT_INDEX]
    session_file = os.path.join(SESSION_FOLDER, f"session-{account}")
    
    if not os.path.exists(session_file):
        return {"error": f"❌ Session introuvable pour {account}"}

    try:
        L.load_session_from_file(account, filename=session_file)
        print(f"✅ Session chargée avec {account}")
    except Exception as e:
        print(f"❌ Erreur de connexion à {account} : {e}")
        return None

    # 📌 Alterne au compte suivant pour la prochaine requête
    CURRENT_ACCOUNT_INDEX = (CURRENT_ACCOUNT_INDEX + 1) % len(INSTAGRAM_ACCOUNTS)

    return L

def wait_before_next_request():
    """ ⏳ Ajoute un délai aléatoire pour éviter les blocages """
    delay = random.randint(30, 120)  # Attente entre 30 et 120 secondes
    print(f"⏳ Pause de {delay} secondes avant la prochaine requête...")
    time.sleep(delay)

@app.route('/scrape/<username>')
def scrape_instagram(username):
    """ 📌 Scrape un compte Instagram en changeant automatiquement de session """
    L = get_instagram_session()
    if not L:
        return jsonify({"error": "Impossible de se connecter à Instagram."})

    try:
        profile = instaloader.Profile.from_username(L.context, username)
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la récupération du profil : {e}"})

    print(f"📊 Récupération des données de {username}...")

    summary = {
        "Username": username,
        "Followers": profile.followers,
        "Following": profile.followees,
        "Posts": profile.mediacount,
        "Engagement Rate": f"{random.uniform(1.5, 5.0):.2f}%"  # Simulé
    }

    wait_before_next_request()  # ⏳ Ajoute un délai

    return jsonify(summary)

@app.route('/')
def home():
    """ 🏠 Page d'accueil """
    return render_template("index.html")

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))  # Render définit automatiquement le PORT
    app.run(host="0.0.0.0", port=port, debug=True)
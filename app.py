from flask import Flask, jsonify
import instaloader
import os
import random
import time

app = Flask(__name__)

# Comptes disponibles pour scraper
INSTAGRAM_ACCOUNTS = ["mart.inette92", "romeol62", "hubertmirgaton"]
CURRENT_ACCOUNT_INDEX = 0  # Index pour alterner les comptes

# Dossier des sessions
SESSION_FOLDER = ".config/instaloader"

# Vérifier si le dossier des sessions existe
if not os.path.exists(SESSION_FOLDER):
    os.makedirs(SESSION_FOLDER)
    print(f"✅ Dossier des sessions créé : {SESSION_FOLDER}")
else:
    print(f"📂 Dossier des sessions déjà existant : {SESSION_FOLDER}")

def list_available_sessions():
    """ Liste les sessions disponibles """
    available_sessions = [f for f in os.listdir(SESSION_FOLDER) if f.startswith("session-")]
    print(f"📂 Sessions disponibles : {available_sessions}")
    return available_sessions

def get_instagram_session():
    """ Charge une session Instagram en alternant entre plusieurs comptes. """
    global CURRENT_ACCOUNT_INDEX
    L = instaloader.Instaloader()

    account = INSTAGRAM_ACCOUNTS[CURRENT_ACCOUNT_INDEX]
    session_file = os.path.join(SESSION_FOLDER, f"session-{account}")
    
    if not os.path.exists(session_file):
        print(f"❌ Session introuvable pour {account}")
        return None

    try:
        L.load_session_from_file(account, filename=session_file)
        print(f"✅ Session chargée avec {account}")
    except Exception as e:
        print(f"❌ Erreur de connexion à {account} : {e}")
        return None

    # Alterne au compte suivant pour la prochaine requête
    CURRENT_ACCOUNT_INDEX = (CURRENT_ACCOUNT_INDEX + 1) % len(INSTAGRAM_ACCOUNTS)

    return L

def wait_before_next_request():
    """ Ajoute un délai aléatoire pour éviter les blocages d'Instagram. """
    delay = random.randint(30, 120)  # Attente aléatoire entre 30 et 120 secondes
    print(f"⏳ Pause de {delay} secondes avant la prochaine requête...")
    time.sleep(delay)

@app.route('/scrape/<username>')
def scrape_instagram(username):
    """ Scrape un compte Instagram en changeant automatiquement de session. """
    L = get_instagram_session()
    if not L:
        return jsonify({"error": "Impossible de se connecter à Instagram."})

    try:
        profile = instaloader.Profile.from_username(L.context, username)
    except Exception as e:
        print(f"❌ Erreur de récupération du profil {username} : {e}")
        return jsonify({"error": f"Erreur lors de la récupération du profil : {e}"})

    print(f"📊 Récupération des données de {username}...")

    # Simulation des statistiques pour éviter de faire trop de requêtes
    summary = {
        "Followers": profile.followers,
        "Following": profile.followees,
        "Posts": profile.mediacount,
        "Username": username,
        "Engagement Rate": f"{random.uniform(1.5, 5.0):.2f}%"  # Simulé pour éviter de se faire bloquer
    }

    wait_before_next_request()  # Pause avant la prochaine requête

    return jsonify(summary)

@app.route('/')
def home():
    """ Page d'accueil pour tester l'API """
    return '''
    <!doctype html>
    <html>
      <head>
        <title>Instagram Scraper</title>
      </head>
      <body>
        <h1>Analyse Instagram</h1>
        <p>Utilisation : /scrape/[nom_utilisateur]</p>
      </body>
    </html>
    '''

if __name__ == '__main__':
    list_available_sessions()  # Affiche les sessions disponibles au démarrage
    app.run(debug=True)
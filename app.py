import os
import shutil
from flask import Flask, request, jsonify, render_template
import instaloader

app = Flask(__name__)

# 📂 Définition du dossier où seront stockées les sessions
SESSION_FOLDER = ".config/instaloader"

# 📌 Vérifier si le dossier existe, sinon le créer
if not os.path.exists(SESSION_FOLDER):
    os.makedirs(SESSION_FOLDER)
    print(f"✅ Dossier des sessions créé : {SESSION_FOLDER}")
else:
    print(f"📂 Dossier des sessions déjà existant : {SESSION_FOLDER}")

# 📌 Liste des fichiers de session disponibles
local_sessions = ["session-mart.inette92", "session-romeol62"]

# 📌 Vérifier et copier les fichiers de session si nécessaire
for session_file in local_sessions:
    local_path = os.path.join(os.getcwd(), session_file)
    session_dest = os.path.join(SESSION_FOLDER, session_file)
    
    if os.path.exists(local_path) and not os.path.exists(session_dest):
        shutil.copy(local_path, session_dest)
        print(f"✅ Session {session_file} copiée dans {SESSION_FOLDER}")
    elif os.path.exists(session_dest):
        print(f"📂 Session {session_file} déjà présente.")

# 📌 Instaloader avec les sessions copiées
L = instaloader.Instaloader()
L.load_session_from_file("mart.inette92", os.path.join(SESSION_FOLDER, "session-mart.inette92"))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/scrape", methods=["GET"])
def scrape():
    username = request.args.get("username")
    
    if not username:
        return jsonify({"error": "Nom d'utilisateur requis"}), 400

    try:
        profile = instaloader.Profile.from_username(L.context, username)

        data = {
            "username": profile.username,
            "followers": profile.followers,
            "following": profile.followees,
            "posts": profile.mediacount,
            "bio": profile.biography,
            "external_url": profile.external_url,
            "is_private": profile.is_private,
        }

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": f"Impossible de récupérer les données : {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
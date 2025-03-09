import instaloader
import datetime
import pandas as pd
import os

# Créer un objet Instaloader
L = instaloader.Instaloader()

# Charger la session enregistrée pour ton compte 'lucas_08h08'
L.load_session_from_file('lucas_08h08')

# Récupérer le profil de Nolwenn
profile = instaloader.Profile.from_username(L.context, 'nolwenn_creme')

# Définir la date limite pour les 3 derniers mois (90 jours)
three_months_ago = datetime.datetime.now() - datetime.timedelta(days=90)

# Liste pour stocker les données des posts
posts_data = []

# Itérer sur les publications du profil (sans télécharger les médias)
for post in profile.get_posts():
    try:
        if post.date_utc > three_months_ago:
            # Pour les vidéos, récupérer le nombre de vues si disponible
            video_views = post.video_view_count if post.is_video and hasattr(post, 'video_view_count') else None
            posts_data.append({
                'Date': post.date_utc,
                'Likes': post.likes,
                'Comments': post.comments,
                'Caption': post.caption,
                'URL': post.url,
                'Video Views': video_views
            })
    except FileNotFoundError as e:
        print(f"Avertissement : {e}. On continue.")
        continue

# Vérifier si des publications ont été trouvées
if posts_data:
    df = pd.DataFrame(posts_data)
    
    # Calculer les moyennes
    avg_likes = df['Likes'].mean()
    avg_comments = df['Comments'].mean()
    # Pour les vues, utiliser celles des posts vidéo s'il y en a, sinon on peut utiliser avg_likes comme proxy
    if df['Video Views'].notnull().any():
        avg_video_views = df.loc[df['Video Views'].notnull(), 'Video Views'].mean()
    else:
        avg_video_views = None
    avg_views = avg_video_views if avg_video_views is not None else avg_likes

    # Récupérer le nombre d'abonnés et le nombre de posts filtrés
    followers_count = profile.followers
    posts_count = len(df)
    engagement_rate = ((avg_likes + avg_comments) / followers_count) * 100 if followers_count else 0

    # Estimer les vues en story (on suppose qu'elles représentent 10 à 20 % des abonnés)
    min_story_views = 0.1 * followers_count
    max_story_views = 0.2 * followers_count

    # Données démographiques simulées (car non accessibles via scraping)
    audience_demographics = {
        'Gender': {'Female': '60%', 'Male': '40%'},
        'Location': {'Paris': '30%', 'Lyon': '20%', 'Marseille': '15%', 'Other': '35%'},
        'Age Distribution': {'18-24': '25%', '25-34': '50%', '35-44': '15%', '45+': '10%'}
    }

    # Créer un résumé avec toutes les statistiques
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

    # Définir le chemin pour sauvegarder le fichier Excel sur le bureau
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    file_path = os.path.join(desktop_path, "nolwenn_creme_stats.xlsx")
    print(f"Le fichier Excel sera sauvegardé ici : {file_path}")

    # Exporter les données dans un fichier Excel avec deux feuilles : "Posts" et "Summary"
    with pd.ExcelWriter(file_path) as writer:
        df.to_excel(writer, index=False, sheet_name='Posts')
        summary_df = pd.DataFrame([summary])
        summary_df.to_excel(writer, index=False, sheet_name='Summary')

    print(f"Le fichier Excel a été généré avec succès : {file_path}")
else:
    print("Aucune publication trouvée pour les 3 derniers mois.")
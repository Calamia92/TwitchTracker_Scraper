# 🎥 TwitchTracker Scraper

Un projet Python permettant de scraper les classements des streamers francophones depuis [TwitchTracker.com](https://twitchtracker.com) et de les visualiser dans une interface web interactive via Streamlit.

---

## 🚀 Fonctionnalités actuelles

✅ Scraping des 10 premières pages du classement FR :  
→ 500 streamers francophones extraits depuis `https://twitchtracker.com/channels/viewership/french`.

✅ Données extraites pour chaque streamer :
- Rang (`rank`)
- Nom (`name`)
- Nombre moyen de spectateurs (`avg_viewers`)
- Heures streamées (`hours_streamed`)
- Nombre maximal de spectateurs (`max_viewers`)
- Minutes totales regardées (`total_minutes_watched`)
- Rang global, gain de followers, followers totaux, vues totales, avatar, lien vers profil…

✅ Sauvegarde dans MongoDB

✅ Interface Streamlit :
- Filtres par nombre de viewers
- Affichage du top 10 par followers
- Tableau interactif
- Graphique dynamique

---

## 📦 Stack technique

- Python 3.10+
- BeautifulSoup4
- Streamlit
- Pandas
- MongoDB
- Dotenv

---

## 🧪 Lancer le projet

```bash
git clone https://github.com/votre-compte/TwitchTracker_Scraper.git
cd TwitchTracker_Scraper

# Création de l'environnement
python -m venv .venv
.\.venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Scraping
python main.py

# Lancer l'interface Streamlit
streamlit run frontend/app.py
````

---

## 🛠️ Fonctionnalités prévues

🔄 **Extension du scraping** :

* Scraper les **profils individuels** des streamers (bio, jeux les plus joués, live récents, etc.)
* Scraper les **classements internationaux** (global, par pays, par jeu…)

🧠 **Ajout de valeur par l’analyse** :

* 📊 Visualisation interactive enrichie (e.g. % de croissance)
* 📈 Suivi temporel (comparaison entre plusieurs scrapes)
* 🤖 **Utilisation d’IA** pour :

  * Estimer les tendances de croissance
  * Recommander des streamers similaires
  * Identifier des anomalies ou des pics inhabituels

🔐 Authentification optionnelle (ex : accès restreint à certaines analyses)

🗓️ **Scraping programmé** (cron ou GitHub Actions) pour mise à jour automatique

---

## 💡 Idée de plus-value IA

> Utiliser des modèles de machine learning simples (regression, clustering ou séries temporelles) pour :

* Prédire le classement d’un streamer dans les semaines à venir
* Détecter les “étoiles montantes”
* Identifier les heures les plus performantes de stream

---

## 🧑‍💻 Auteur

Projet développé par Boubaker, Aya et Hicham dans le cadre d'un projet scolaire Python & Scraping.


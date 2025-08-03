import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import time
import re
import sys
import os

# Ajout du répertoire parent pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.mongo_client import db

def extract_profile_data(profile_url, streamer_name):
    """
    Scrape les données détaillées d'un profil streamer TwitchTracker
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        print(f"🔍 Scraping profil : {streamer_name} - {profile_url}")
        response = requests.get(profile_url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extraction des données
        profile_data = {
            "name": streamer_name,
            "profile_url": profile_url,
            "scraped_at": datetime.now(timezone.utc).isoformat()
        }
        
        # 1. Bio/Description - SÉLECTEURS CORRIGÉS
        bio = None
        
        # Chercher dans la section profil streamer
        bio_div = soup.find("div", style=lambda x: x and "word-wrap:break-word" in x)
        if bio_div:
            bio = bio_div.get_text(strip=True)
            # Nettoyer l'email crypté
            bio = re.sub(r'\[email protected\]', '', bio)
        
        profile_data["bio"] = bio
        
        # 2. Top jeux - SÉLECTEURS CORRIGÉS basés sur la vraie structure HTML
        top_games = []
        
        # Chercher le container des jeux directement par ID
        games_container = soup.find("div", id="channel-games")
        if games_container:
            game_links = games_container.find_all("a", class_="entity")
            for game_link in game_links[:5]:  # Top 5
                # Nom du jeu dans l'attribut title de la div ou img
                title_div = game_link.find("div", title=True)
                if title_div and title_div.get("title"):
                    game_name = title_div.get("title")
                    
                    # Heures dans le span avec class "to-time"
                    hours = "N/A"
                    time_span = game_link.find("span", class_="to-time")
                    if time_span:
                        hours = time_span.get_text(strip=True)
                    
                    if game_name:
                        top_games.append({
                            "game": game_name,
                            "hours": hours
                        })
        
        profile_data["top_games"] = top_games
        
        # 3. Streams récents - SÉLECTEURS CORRIGÉS basés sur la vraie structure HTML
        recent_streams = []
        
        # Chercher le container des streams directement par ID
        streams_container = soup.find("div", id="channel-streams")
        if streams_container:
            stream_links = streams_container.find_all("a", class_="entity-line")
            for stream_link in stream_links[:10]:  # 10 derniers
                # Date dans l'attribut data-dt
                date = "N/A"
                date_div = stream_link.find("div", attrs={"data-dt": True})
                if date_div:
                    date = date_div.get("data-dt")
                
                # Viewers max dans le span avec class "to-number-lg"
                viewers = "0"
                viewers_divs = stream_link.find_all("div", class_="to-number-lg")
                if viewers_divs:
                    viewers = viewers_divs[0].get_text(strip=True)
                
                # Durée dans le span avec class "to-time-lg"
                duration = "0h"
                duration_div = stream_link.find("div", class_="to-time-lg")
                if duration_div:
                    duration = duration_div.get_text(strip=True)
                
                # Jeux depuis les images avec attribut title
                games = []
                game_imgs = stream_link.find_all("img", title=True)
                for img in game_imgs:
                    title = img.get("title")
                    if title:
                        games.append(title)
                
                main_game = games[0] if games else "Unknown"
                
                recent_streams.append({
                    "date": date,
                    "game": main_game,
                    "duration": duration,
                    "max_viewers": viewers,
                    "all_games": games
                })
        
        profile_data["recent_streams"] = recent_streams
        
        # 4. Statistiques depuis les sections g-x-s-block
        stats = {}
        
        # Chercher les blocs de statistiques lifetime
        stat_blocks = soup.find_all("div", class_="g-x-s-block")
        for block in stat_blocks:
            # Valeur dans to-number ou le premier div
            value_div = block.find("div", class_="to-number") or block.find("div", class_="g-x-s-value")
            if value_div:
                value = value_div.get_text(strip=True)
                
                # Label dans g-x-s-label
                label_div = block.find("div", class_="g-x-s-label")
                if label_div:
                    label = label_div.get_text(strip=True).lower().replace(" ", "_")
                    if label and value:
                        stats[label] = value
        
        # Ajouter les stats des tableaux (Average Stream, Various Metrics)
        tables = soup.find_all("table", class_="table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) == 2:
                    key = cols[0].get_text(strip=True).lower().replace(" ", "_").replace(":", "")
                    value = cols[1].get_text(strip=True)
                    if key and value:
                        stats[key] = value
        
        profile_data["additional_stats"] = stats
        
        # 5. Informations du channel depuis la section profil
        channel_info = {}
        
        # Chercher dans la section "Streamer Profile"
        profile_section = soup.find("div", string="Streamer Profile")
        if profile_section:
            profile_container = profile_section.parent.parent
            
            # Language
            lang_link = profile_container.find("a", href=lambda x: x and "/languages/" in x)
            if lang_link:
                channel_info["language"] = lang_link.get_text(strip=True)
            
            # Created date
            date_spans = profile_container.find_all("span", class_="to-date")
            if date_spans:
                channel_info["created_date"] = date_spans[0].get_text(strip=True)
            
            # Partner status
            partner_spans = profile_container.find_all("span", class_="label-soft")
            for span in partner_spans:
                text = span.get_text(strip=True)
                if text in ["Partner", "Affiliate"]:
                    channel_info["status"] = text
        
        profile_data["channel_info"] = channel_info
        
        return profile_data
        
    except requests.RequestException as e:
        print(f"❌ Erreur réseau pour {streamer_name}: {e}")
        return None
    except Exception as e:
        print(f"❌ Erreur parsing pour {streamer_name}: {e}")
        return None

def scrape_all_profiles_fr():
    """
    Récupère tous les profile_url depuis MongoDB et scrape les profils détaillés
    """
    # Récupération des streamers depuis MongoDB
    collection = db["viewership_fr"]
    streamers = list(collection.find({}, {"name": 1, "profile_url": 1, "rank": 1}))
    
    print(f"🎯 {len(streamers)} streamers trouvés dans la base")
    
    profiles_data = []
    errors = 0
    
    for i, streamer in enumerate(streamers, 1):
        name = streamer.get("name")
        profile_url = streamer.get("profile_url")
        rank = streamer.get("rank")
        
        if not profile_url:
            print(f"⚠️ Pas d'URL pour {name}")
            continue
            
        print(f"📊 [{i}/{len(streamers)}] Rank #{rank} - {name}")
        
        profile_data = extract_profile_data(profile_url, name)
        
        if profile_data:
            profile_data["rank"] = rank  # Ajout du rang
            profiles_data.append(profile_data)
            
            bio_info = "✅ Bio trouvée" if profile_data.get('bio') else "❌ Pas de bio"
            games_count = len(profile_data.get('top_games', []))
            streams_count = len(profile_data.get('recent_streams', []))
            stats_count = len(profile_data.get('additional_stats', {}))
            
            print(f"✅ Profil récupéré : {bio_info}, {games_count} jeux, {streams_count} streams, {stats_count} stats")
        else:
            errors += 1
            print(f"❌ Échec du scraping pour {name}")
        
        # Pause entre les requêtes pour éviter d'être bloqué
        if i % 10 == 0:
            print(f"⏸️ Pause après {i} profils...")
            time.sleep(3)
        else:
            time.sleep(1.5)
    
    print(f"\n🎉 Scraping terminé !")
    print(f"✅ Profils récupérés : {len(profiles_data)}")
    print(f"❌ Erreurs : {errors}")
    
    return profiles_data

if __name__ == "__main__":
    # Test sur un seul profil
    test_url = "https://twitchtracker.com/zerator"
    test_data = extract_profile_data(test_url, "Zerator")
    
    if test_data:
        print("🧪 Test réussi !")
        bio = test_data.get('bio', 'N/A')
        print(f"Bio: {bio[:100] if bio else 'Aucune bio trouvée'}...")
        print(f"Top jeux: {len(test_data.get('top_games', []))}")
        print(f"Streams récents: {len(test_data.get('recent_streams', []))}")
        print(f"Stats additionnelles: {len(test_data.get('additional_stats', {}))}")
        
        # Afficher un exemple de jeu
        games = test_data.get('top_games', [])
        if games:
            print(f"Premier jeu: {games[0]}")
        
        # Afficher un exemple de stream
        streams = test_data.get('recent_streams', [])
        if streams:
            print(f"Premier stream: {streams[0]}")
    else:
        print("❌ Test échoué")
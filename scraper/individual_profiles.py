import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re

def scrape_individual_profile(profile_url):
    """
    Scrape le profil individuel d'un streamer
    
    Args:
        profile_url (str): URL du profil (ex: https://twitchtracker.com/ibai)
    
    Returns:
        dict: Données du profil extrait
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(profile_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extraction du nom du streamer depuis l'URL
        streamer_name = profile_url.split('/')[-1]
        
        # 1. Biographie
        bio = extract_bio(soup)
        
        # 2. Top games joués récemment
        top_games = extract_top_games(soup)
        
        # 3. Lives récents
        recent_streams = extract_recent_streams(soup)
        
        # 4. Stats mensuelles (si disponibles)
        monthly_stats = extract_monthly_stats(soup)
        
        profile_data = {
            "streamer_name": streamer_name,
            "profile_url": profile_url,
            "bio": bio,
            "top_games": top_games,
            "recent_streams": recent_streams,
            "monthly_stats": monthly_stats,
            "scraped_at": datetime.now().isoformat()
        }
        
        return profile_data
        
    except Exception as e:
        print(f"[❌] Erreur lors du scraping de {profile_url}: {e}")
        return None

def extract_bio(soup):
    """Extraire la biographie du streamer"""
    try:
        # Chercher dans différents sélecteurs possibles pour la bio
        bio_selectors = [
            ".description",
            ".bio",
            ".about",
            "[data-bio]",
            ".stream-description"
        ]
        
        for selector in bio_selectors:
            bio_element = soup.select_one(selector)
            if bio_element:
                return bio_element.get_text(strip=True)
        
        return None
    except Exception:
        return None

def extract_top_games(soup):
    """Extraire les jeux joués récemment"""
    try:
        games = []
        
        # Chercher les jeux dans les sections typiques
        game_selectors = [
            ".game-list .game-item",
            ".games .game",
            ".top-games .game",
            ".game-card"
        ]
        
        for selector in game_selectors:
            game_elements = soup.select(selector)
            if game_elements:
                for game in game_elements[:10]:  # Limiter à 10 jeux max
                    game_name = game.get_text(strip=True)
                    if game_name:
                        games.append(game_name)
                break
        
        return games if games else None
    except Exception:
        return None

def extract_recent_streams(soup):
    """Extraire les informations sur les lives récents"""
    try:
        streams = []
        
        # Chercher les streams récents
        stream_selectors = [
            ".stream-list .stream-item",
            ".recent-streams .stream",
            ".streams .stream-row"
        ]
        
        for selector in stream_selectors:
            stream_elements = soup.select(selector)
            if stream_elements:
                for stream in stream_elements[:5]:  # Limiter à 5 streams récents
                    stream_info = {}
                    
                    # Titre du stream
                    title_elem = stream.select_one(".title, .stream-title, h3, h4")
                    if title_elem:
                        stream_info["title"] = title_elem.get_text(strip=True)
                    
                    # Date/durée
                    date_elem = stream.select_one(".date, .duration, .time")
                    if date_elem:
                        stream_info["date_duration"] = date_elem.get_text(strip=True)
                    
                    # Nombre de viewers
                    viewers_elem = stream.select_one(".viewers, .view-count")
                    if viewers_elem:
                        stream_info["viewers"] = viewers_elem.get_text(strip=True)
                    
                    if stream_info:
                        streams.append(stream_info)
                break
        
        return streams if streams else None
    except Exception:
        return None

def extract_monthly_stats(soup):
    """Extraire les statistiques mensuelles"""
    try:
        stats = {}
        
        # Chercher les stats dans différents formats
        stats_selectors = [
            ".stats-container",
            ".monthly-stats",
            ".statistics",
            ".metrics"
        ]
        
        for selector in stats_selectors:
            stats_container = soup.select_one(selector)
            if stats_container:
                # Extraire les valeurs numériques et leurs labels
                stat_items = stats_container.select(".stat-item, .metric, .stat")
                
                for item in stat_items:
                    label_elem = item.select_one(".label, .stat-label, .metric-label")
                    value_elem = item.select_one(".value, .stat-value, .metric-value")
                    
                    if label_elem and value_elem:
                        label = label_elem.get_text(strip=True)
                        value = value_elem.get_text(strip=True)
                        stats[label] = value
                
                if stats:
                    break
        
        return stats if stats else None
    except Exception:
        return None

def scrape_profiles_from_world_data(world_streamers_data, max_profiles=50):
    """
    Scraper les profils individuels à partir des données du Top 500 mondial
    
    Args:
        world_streamers_data (list): Liste des streamers du Top 500 mondial
        max_profiles (int): Nombre maximum de profils à scraper
    
    Returns:
        list: Liste des profils scrapés
    """
    profiles_data = []
    
    print(f"🔍 Début du scraping des profils individuels...")
    print(f"📊 Cible: {min(len(world_streamers_data), max_profiles)} profils")
    print("=" * 60)
    
    for i, streamer in enumerate(world_streamers_data[:max_profiles], 1):
        profile_url = streamer.get('profile_url')
        streamer_name = streamer.get('name', 'Inconnu')
        
        if not profile_url:
            print(f"[⚠️] #{i} {streamer_name}: URL de profil manquante")
            continue
        
        print(f"🔎 #{i:2d}/{max_profiles} Scraping: {streamer_name}")
        print(f"    URL: {profile_url}")
        
        # Scraper le profil individuel
        profile_data = scrape_individual_profile(profile_url)
        
        if profile_data:
            # Ajouter les infos de base du classement mondial
            profile_data["world_rank"] = streamer.get('rank')
            profile_data["avg_viewers"] = streamer.get('avg_viewers')
            profiles_data.append(profile_data)
            print(f"    ✅ Profil extrait avec succès")
        else:
            print(f"    ❌ Échec de l'extraction")
        
        # Pause pour éviter d'être bloqué
        time.sleep(2)
        
        # Affichage d'un résumé tous les 10 profils
        if i % 10 == 0:
            print(f"\n📈 Progression: {i}/{max_profiles} profils traités")
            print(f"✅ Réussis: {len(profiles_data)}")
            print("-" * 40)
    
    print(f"\n🎉 Scraping des profils terminé !")
    print(f"📊 Total: {len(profiles_data)} profils extraits sur {max_profiles} tentatives")
    
    return profiles_data

if __name__ == "__main__":
    # Test avec une URL de profil exemple
    test_url = "https://twitchtracker.com/ibai"
    print(f"🧪 Test du scraper de profil avec: {test_url}")
    
    profile = scrape_individual_profile(test_url)
    if profile:
        print("\n✅ Test réussi !")
        print(f"Nom: {profile.get('streamer_name')}")
        print(f"Bio: {profile.get('bio', 'Non trouvée')[:100]}...")
        print(f"Jeux: {profile.get('top_games', [])[:3]}")
    else:
        print("\n❌ Test échoué")

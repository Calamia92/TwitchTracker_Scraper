import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

def scrape_viewership_world():
    """
    Scrape le Top 500 MONDIAL des streamers Twitch
    URL: https://twitchtracker.com/channels/viewership
    """
    base_url = "https://twitchtracker.com/channels/viewership"
    headers = {"User-Agent": "Mozilla/5.0"}

    all_data = []
    total_skipped = 0

    # Top 500 = 10 pages de 50 streamers chacune
    for page in range(1, 11):  # Pages 1 à 10 incluses
        url = f"{base_url}?page={page}" if page > 1 else base_url
        print(f"🌍 Scraping page {page} (Top 500 World)...")

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        rows = soup.select("table tbody tr")
        print(f"📄 Page {page} : {len(rows)} lignes détectées")

        for i, row in enumerate(rows, start=1):
            try:
                cols = row.find_all("td")
                
                # Ignorer les lignes vides ou de publicité (sans affichage d'erreur)
                if len(cols) < 6:
                    continue
                
                # Vérifier si c'est une vraie ligne de données (doit avoir un rank numérique)
                rank_cell = cols[0].text.strip().replace("#", "")
                if not rank_cell or not rank_cell.isdigit():
                    continue
                
                rank = int(rank_cell)

                # Informations du profil
                profile_link = cols[1].find("a")["href"]
                profile_url = f"https://twitchtracker.com{profile_link}"
                avatar_img = cols[1].find("img")
                avatar_url = avatar_img["src"] if avatar_img else None
                
                # Nom du streamer
                name = cols[2].text.strip()

                # Données de viewership
                avg_viewers = cols[3].text.strip()
                hours_streamed_span = cols[4].find("span")
                hours_streamed = hours_streamed_span.text.strip() if hours_streamed_span else cols[4].text.strip()
                max_viewers = cols[5].text.strip()
                total_minutes_watched = cols[6].text.strip() if len(cols) > 6 else None

                # Données supplémentaires (optionnelles)
                global_rank = cols[7].text.strip() if len(cols) > 7 else None
                followers_gain = cols[8].text.strip().lstrip("+") if len(cols) > 8 else None
                total_followers = cols[9].text.strip() if len(cols) > 9 else None
                total_views = cols[10].text.strip() if len(cols) > 10 and "--" not in cols[10].text else None

                # Données structurées
                streamer_data = {
                    "rank": rank,
                    "name": name,
                    "profile_url": profile_url,
                    "avatar_url": avatar_url,
                    "avg_viewers": avg_viewers,
                    "hours_streamed": hours_streamed,
                    "max_viewers": max_viewers,
                    "total_minutes_watched": total_minutes_watched,
                    "global_rank": global_rank,
                    "followers_gain": followers_gain,
                    "total_followers": total_followers,
                    "total_views": total_views,
                    "page": page,
                    "region": "world",  # Identifiant pour différencier du scraping FR
                    "scraped_at": datetime.utcnow().isoformat()
                }

                all_data.append(streamer_data)

                # Log pour le debug (optionnel)
                if rank <= 10:  # Afficher les 10 premiers pour vérification
                    print(f"  #{rank} {name} - {avg_viewers} viewers avg")

            except Exception as e:
                print(f"[❌] Exception à la page {page}, ligne {i} : {e}")
                total_skipped += 1
                continue

        # Pause entre les pages pour éviter d'être bloqué
        time.sleep(1.5)

    print(f"\n🌍 ✅ Scraping Top 500 World terminé : {len(all_data)} streamers récupérés")
    print(f"🚫 Total ignoré/skippé : {total_skipped} lignes")
    
    return all_data

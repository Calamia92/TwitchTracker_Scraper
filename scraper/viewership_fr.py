import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time  # ⬅️ Ajout ici

def scrape_viewership_fr():
    base_url = "https://twitchtracker.com/channels/viewership/french"
    headers = {"User-Agent": "Mozilla/5.0"}

    all_data = []
    total_skipped = 0

    for page in range(1, 11):  # Pages 1 à 10 incluses
        url = f"{base_url}?page={page}" if page > 1 else base_url
        print(f"🔎 Scraping page {page}...")

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
                rank_raw = cols[0].text.strip().replace("#", "")
                if not rank_raw or not rank_raw.isdigit():
                    continue
                
                rank = int(rank_raw)

                profile_link = cols[1].find("a")["href"]
                profile_url = f"https://twitchtracker.com{profile_link}"
                avatar_url = cols[1].find("img")["src"]
                name = cols[2].text.strip()

                avg_viewers = cols[3].text.strip()
                hours_streamed_span = cols[4].find("span")
                hours_streamed = hours_streamed_span.text.strip() if hours_streamed_span else cols[4].text.strip()
                max_viewers = cols[5].text.strip()
                total_minutes_watched = cols[6].text.strip() if len(cols) > 6 else None

                global_rank = cols[7].text.strip() if len(cols) > 7 else None
                followers_gain = cols[8].text.strip().lstrip("+") if len(cols) > 8 else None
                total_followers = cols[9].text.strip() if len(cols) > 9 else None
                total_views = cols[10].text.strip() if "--" not in cols[10].text else None

                all_data.append({
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
                    "scraped_at": datetime.utcnow().isoformat()
                })

            except Exception as e:
                print(f"[❌] Exception à la page {page}, ligne {i} : {e}")
                total_skipped += 1
                continue

        time.sleep(1.5)  # ⏳ Pause entre les pages

    print(f"\n✅ Scraping terminé : {len(all_data)} streamers récupérés")
    print(f"🚫 Total ignoré/skippé : {total_skipped} lignes")
    return all_data
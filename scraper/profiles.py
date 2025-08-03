import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from db.mongo_client import db
import time
import re
import logging

# Setup logger
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def clean_number(text):
    """Nettoyer et convertir un texte numérique en int si possible"""
    if not text:
        return None
    text = text.replace(",", "").replace(" ", "").replace("K", "*1e3").replace("M", "*1e6")
    try:
        return int(eval(text))
    except Exception:
        return text.strip()

def extract_bio(soup):
    bio_div = soup.find("div", style=lambda x: x and "word-wrap:break-word" in x)
    if bio_div:
        bio = bio_div.get_text(strip=True)
        return re.sub(r'\[email protected\]', '', bio)
    return None

def extract_top_games(soup):
    games = []
    container = soup.find("div", id="channel-games")
    if container:
        links = container.find_all("a", class_="entity")
        for link in links[:5]:
            title_div = link.find("div", title=True)
            game_name = title_div.get("title") if title_div else None
            hours = link.find("span", class_="to-time")
            if game_name:
                games.append({
                    "game": game_name,
                    "hours": hours.get_text(strip=True) if hours else "N/A"
                })
    return games

def extract_recent_streams(soup):
    streams = []
    container = soup.find("div", id="channel-streams")
    if container:
        links = container.find_all("a", class_="entity-line")
        for link in links[:10]:
            date = link.find("div", attrs={"data-dt": True})
            viewers_div = link.find_all("div", class_="to-number-lg")
            duration_div = link.find("div", class_="to-time-lg")
            games = [img.get("title") for img in link.find_all("img", title=True) if img.get("title")]
            streams.append({
                "date": date.get("data-dt") if date else "N/A",
                "game": games[0] if games else "Unknown",
                "duration": duration_div.get_text(strip=True) if duration_div else "0h",
                "max_viewers": viewers_div[0].get_text(strip=True) if viewers_div else "0",
                "all_games": games
            })
    return streams

def extract_additional_stats(soup):
    stats = {}
    blocks = soup.find_all("div", class_="g-x-s-block")
    for block in blocks:
        value = block.find("div", class_="to-number") or block.find("div", class_="g-x-s-value")
        label = block.find("div", class_="g-x-s-label")
        if value and label:
            key = label.get_text(strip=True).lower().replace(" ", "_")
            stats[key] = clean_number(value.get_text(strip=True))
    tables = soup.find_all("table", class_="table")
    for table in tables:
        for row in table.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) == 2:
                key = cols[0].get_text(strip=True).lower().replace(" ", "_").replace(":", "")
                stats[key] = clean_number(cols[1].get_text(strip=True))
    return stats

def extract_channel_info(soup):
    info = {}
    section = soup.find("div", string="Streamer Profile")
    if section:
        container = section.parent.parent
        lang = container.find("a", href=lambda x: x and "/languages/" in x)
        if lang:
            info["language"] = lang.get_text(strip=True)
        date_spans = container.find_all("span", class_="to-date")
        if date_spans:
            info["created_date"] = date_spans[0].get_text(strip=True)
        statuses = container.find_all("span", class_="label-soft")
        for s in statuses:
            status = s.get_text(strip=True)
            if status in ["Partner", "Affiliate"]:
                info["status"] = status
    return info

def extract_profile_data(profile_url, streamer_name, max_retries=2):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for attempt in range(1, max_retries + 1):
        try:
            logging.info(f"🔍 Scraping : {streamer_name} - {profile_url} (tentative {attempt})")
            response = requests.get(profile_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            return {
                "name": streamer_name,
                "profile_url": profile_url,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "bio": extract_bio(soup),
                "top_games": extract_top_games(soup),
                "recent_streams": extract_recent_streams(soup),
                "additional_stats": extract_additional_stats(soup),
                "channel_info": extract_channel_info(soup)
            }

        except requests.exceptions.HTTPError as e:
            if response.status_code == 429 and attempt < max_retries:
                logging.warning(f"⏳ Trop de requêtes (429). Attente 60s avant retry...")
                time.sleep(60)
            else:
                logging.error(f"❌ Erreur HTTP ({streamer_name}): {e}")
                break
        except Exception as e:
            logging.error(f"❌ Erreur scraping/parsing ({streamer_name}): {e}")
            break

    return None

def scrape_all_profiles_fr():
    streamers = list(db["viewership_fr"].find({}, {"name": 1, "profile_url": 1, "rank": 1}))
    logging.info(f"🎯 {len(streamers)} streamers français trouvés dans la base")

    profiles_data = []
    for i, streamer in enumerate(streamers, 1):
        name = streamer.get("name")
        url = streamer.get("profile_url")
        rank = streamer.get("rank")

        if not url:
            logging.warning(f"⚠️ Pas d'URL pour {name}")
            continue

        logging.info(f"📊 [{i}/{len(streamers)}] Rank #{rank} - {name}")
        data = extract_profile_data(url, name)

        if data:
            data["rank"] = rank
            profiles_data.append(data)
            logging.info(f"✅ Profil {name} récupéré")
        else:
            logging.error(f"❌ Échec pour {name}")

        time.sleep(1.5)

    return profiles_data

def scrape_all_profiles_world(limit=None):
    query = db["viewership_world"].find({}, {"name": 1, "profile_url": 1, "rank": 1}).sort("rank", 1)
    if limit:
        query = query.limit(limit)

    streamers = list(query)
    logging.info(f"🌍 {len(streamers)} streamers mondiaux trouvés dans la base")

    profiles_data = []
    for i, streamer in enumerate(streamers, 1):
        name = streamer.get("name")
        url = streamer.get("profile_url")
        rank = streamer.get("rank")

        if not url:
            logging.warning(f"⚠️ Pas d'URL pour {name}")
            continue

        logging.info(f"🌐 [{i}/{len(streamers)}] Rank #{rank} - {name}")
        data = extract_profile_data(url, name)

        if data:
            data["rank"] = rank
            profiles_data.append(data)
            logging.info(f"✅ Profil {name} récupéré")
        else:
            logging.error(f"❌ Échec pour {name}")

        time.sleep(1.5)

    return profiles_data

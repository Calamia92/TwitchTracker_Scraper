import requests
from bs4 import BeautifulSoup

def analyze_twitch_tracker_structure():
    """
    Analyse la structure HTML réelle d'une page TwitchTracker
    """
    url = "https://twitchtracker.com/zerator"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    print("🔍 ANALYSE DE LA STRUCTURE HTML")
    print("=" * 50)
    
    # Sauvegarde du HTML pour analyse
    with open("zerator_page.html", "w", encoding="utf-8") as f:
        f.write(soup.prettify())
    
    print("✅ HTML sauvegardé dans 'zerator_page.html'")
    
    # Recherche de patterns communs
    print("\n📊 ÉLÉMENTS TROUVÉS :")
    
    # Toutes les divs avec des classes
    divs_with_class = soup.find_all("div", class_=True)
    print(f"- Divs avec classes : {len(divs_with_class)}")
    
    # Tables
    tables = soup.find_all("table")
    print(f"- Tables : {len(tables)}")
    if tables:
        for i, table in enumerate(tables[:3]):
            print(f"  Table {i+1}: {table.get('class', 'no-class')}")
    
    # Scripts (peut contenir des données JSON)
    scripts = soup.find_all("script")
    print(f"- Scripts : {len(scripts)}")
    
    # Recherche de texte spécifique
    if "zerator" in soup.get_text().lower():
        print("✅ Nom du streamer trouvé dans le HTML")
    else:
        print("❌ Nom du streamer PAS trouvé dans le HTML")

if __name__ == "__main__":
    analyze_twitch_tracker_structure()
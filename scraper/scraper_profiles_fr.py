from scraper.profiles_fr import scrape_all_profiles_fr
from db.insert_data import insert_profiles_data

def main():
    print("🚀 Démarrage du scraping des profils détaillés FR...")
    
    # Scraping des profils
    profiles_data = scrape_all_profiles_fr()
    
    # Insertion en base
    insert_profiles_data(profiles_data)
    
    print("✅ Scraping des profils terminé !")

if __name__ == "__main__":
    main()
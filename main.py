from scraper.viewership_fr import scrape_viewership_fr
from scraper.viewership_world import scrape_viewership_world
from scraper.individual_profiles import scrape_profiles_from_world_data
from db.insert_data import insert_viewership_data, insert_viewership_world_data, insert_individual_profiles_data

def scrape_france():
    """Scraper uniquement les streamers français"""
    print("\n🇫🇷 SCRAPING FRANCE")
    print("-" * 30)
    data_fr = scrape_viewership_fr()
    insert_viewership_data(data_fr)
    print("✅ Données FR insérées dans MongoDB !")
    return data_fr

def scrape_world():
    """Scraper uniquement le Top 500 mondial"""
    print("\n🌍 SCRAPING TOP 500 MONDIAL")
    print("-" * 30)
    data_world = scrape_viewership_world()
    insert_viewership_world_data(data_world)
    print("✅ Données mondiales insérées dans MongoDB !")
    return data_world

def scrape_individual_profiles():
    """Scraper les profils individuels des streamers du Top 500 mondial"""
    print("\n👤 SCRAPING PROFILS INDIVIDUELS")
    print("-" * 30)
    
    # D'abord récupérer les données du Top 500 mondial
    print("📋 Récupération des données du Top 500 mondial...")
    world_data = scrape_viewership_world()
    
    if not world_data:
        print("❌ Impossible de récupérer les données du Top 500 mondial")
        return []
    
    # Scraper les profils individuels (limité à 50 pour éviter les timeouts)
    profiles_data = scrape_profiles_from_world_data(world_data, max_profiles=50)
    
    # Sauvegarder en base
    if profiles_data:
        insert_individual_profiles_data(profiles_data)
        print("✅ Profils individuels insérés dans MongoDB !")
    
    return profiles_data

def scrape_all():
    """Scraper France + Mondial"""
    print("🚀 SCRAPING COMPLET (France + Mondial)")
    print("="*50)
    
    data_fr = scrape_france()
    data_world = scrape_world()
    
    print("\n" + "="*50)
    print("🎉 SCRAPING TERMINÉ AVEC SUCCÈS !")
    print(f"📊 France: {len(data_fr)} streamers")
    print(f"🌍 Mondial: {len(data_world)} streamers")
    
    return data_fr, data_world

def main():
    print("🎥 TWITCHTRACKER SCRAPER")
    print("="*50)
    print("1. Scraper France uniquement")
    print("2. Scraper Top 500 Mondial uniquement") 
    print("3. Scraper TOUT (France + Mondial)")
    print("4. Scraper Profils Individuels (Top 50 mondial)")
    print("="*50)
    
    while True:
        try:
            choice = input("\nChoix (1-4): ").strip()
            
            if choice == "1":
                scrape_france()
                break
            elif choice == "2":
                scrape_world()
                break
            elif choice == "3":
                scrape_all()
                break
            elif choice == "4":
                scrape_individual_profiles()
                break
            else:
                print("❌ Choix invalide. Tapez 1, 2, 3 ou 4.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Scraping annulé.")
            break
        except Exception as e:
            print(f"❌ Erreur: {e}")
            break

if __name__ == "__main__":
    main()
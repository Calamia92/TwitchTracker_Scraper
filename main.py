from scraper.viewership_fr import scrape_viewership_fr
from scraper.viewership_world import scrape_viewership_world
from scraper.profiles import scrape_all_profiles_fr, scrape_all_profiles_world
from db.insert_data import (
    insert_viewership_data,
    insert_viewership_world_data,
    insert_profiles_data
)

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

def scrape_profiles_fr():
    """Scraper les profils détaillés des streamers français"""
    print("\n👤 SCRAPING PROFILS FR")
    print("-" * 30)
    profiles_data = scrape_all_profiles_fr()
    insert_profiles_data(profiles_data)
    print("✅ Profils détaillés FR insérés dans MongoDB !")
    return profiles_data

def scrape_profiles_world():
    """Scraper les profils détaillés des streamers mondiaux"""
    print("\n🌐 SCRAPING PROFILS MONDIAUX")
    print("-" * 30)
    profiles_data = scrape_all_profiles_world(limit=50)  # Limite optionnelle
    insert_profiles_data(profiles_data)
    print("✅ Profils détaillés MONDIAUX insérés dans MongoDB !")
    return profiles_data

def scrape_all():
    """Scraper France + Mondial"""
    print("🚀 SCRAPING COMPLET (France + Mondial)")
    print("=" * 50)
    data_fr = scrape_france()
    data_world = scrape_world()
    print("\n" + "=" * 50)
    print("🎉 SCRAPING TERMINÉ AVEC SUCCÈS !")
    print(f"📊 France: {len(data_fr)} streamers")
    print(f"🌍 Mondial: {len(data_world)} streamers")
    return data_fr, data_world

def scrape_everything():
    """Scraper tout : Classements + Profils"""
    print("🚀 SCRAPING COMPLET (Classements + Profils)")
    print("=" * 50)
    data_fr = scrape_france()
    data_world = scrape_world()
    profiles_fr = scrape_profiles_fr()
    profiles_world = scrape_profiles_world()
    print("\n🎉 SCRAPING TERMINÉ AVEC SUCCÈS !")
    print(f"📊 Classement FR: {len(data_fr)} streamers")
    print(f"🌍 Classement World: {len(data_world)} streamers")
    print(f"👤 Profils FR: {len(profiles_fr)}")
    print(f"🌐 Profils World: {len(profiles_world)}")


def main():
    print("🎥 TWITCHTRACKER SCRAPER")
    print("=" * 50)
    print("1. Scraper France uniquement")
    print("2. Scraper Top 500 Mondial uniquement")
    print("3. Scraper TOUT (France + Mondial)")
    print("4. Scraper Profils FR (viewership_fr)")
    print("5. Scraper Profils MONDIAUX (viewership_world)")
    print("6. 🔁 Tout scraper (Classements + Profils)")
    print("=" * 50)

    while True:
        try:
            choice = input("\nChoix (1-5): ").strip()

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
                scrape_profiles_fr()
                break
            elif choice == "5":
                scrape_profiles_world()
                break
            elif choice == "6":
                scrape_everything()
                break
            else:
                print("❌ Choix invalide. Tapez un nombre entre 1 et 5.")

        except KeyboardInterrupt:
            print("\n\n👋 Scraping annulé.")
            break
        except Exception as e:
            print(f"❌ Erreur: {e}")
            break

if __name__ == "__main__":
    main()

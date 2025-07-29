from scraper.viewership_fr import scrape_viewership_fr
from db.insert_data import insert_viewership_data

data = scrape_viewership_fr()
insert_viewership_data(data)
print("✅ Données insérées dans MongoDB !")
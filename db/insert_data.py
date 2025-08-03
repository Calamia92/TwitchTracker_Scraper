from db.mongo_client import db

def insert_data(collection_name, data, label=None):
    """Insérer des données dans MongoDB avec suppression préalable"""
    try:
        collection = db[collection_name]
        collection.delete_many({})
        if data:
            collection.insert_many(data)
            print(f"✅ {len(data)} {label or 'documents'} insérés dans '{collection_name}'")
        else:
            print(f"⚠️ Aucune donnée à insérer dans '{collection_name}'")
    except Exception as e:
        print("❌ Erreur MongoDB: Impossible de se connecter à la base de données")
        print("💡 Solution: Démarrez MongoDB avec la commande 'mongod' dans un autre terminal")
        print("🔧 Ou installez MongoDB: https://www.mongodb.com/try/download/community")
        print(f"Détail de l'erreur : {e}")

def insert_viewership_data(data):
    insert_data("viewership_fr", data, "streamers français")

def insert_viewership_world_data(data):
    insert_data("viewership_world", data, "streamers du Top 500 mondial")

def insert_profiles_data(data):
    insert_data("profiles", data, "profils")

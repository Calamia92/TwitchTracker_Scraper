from db.mongo_client import db

def insert_data(collection_name, data, label=None):
    """Insère ou met à jour des documents dans MongoDB (par nom)"""
    try:
        collection = db[collection_name]
        inserted_count = 0
        updated_count = 0

        for doc in data:
            result = collection.replace_one(
                {"name": doc.get("name")},
                doc,
                upsert=True
            )
            if result.matched_count:
                updated_count += 1
            else:
                inserted_count += 1

        print(f"✅ {inserted_count} nouveaux {label or 'documents'} insérés")
        print(f"🔁 {updated_count} {label or 'documents'} mis à jour dans '{collection_name}'")

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

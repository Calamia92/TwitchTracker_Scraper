from db.mongo_client import db

def insert_viewership_data(data):
    """Insérer les données des streamers français dans MongoDB"""
    try:
        collection = db["viewership_fr"]
        collection.delete_many({})
        collection.insert_many(data)
        print(f"✅ {len(data)} streamers français insérés dans MongoDB")
    except Exception as e:
        print(f"❌ Erreur MongoDB: Impossible de se connecter à la base de données")
        print(f"💡 Solution: Démarrez MongoDB avec la commande 'mongod' dans un autre terminal")
        print(f"🔧 Ou installez MongoDB: https://www.mongodb.com/try/download/community")

def insert_viewership_world_data(data):
    """Insérer les données du Top 500 mondial dans MongoDB"""
    try:
        collection = db["viewership_world"]
        collection.delete_many({})  # Efface les anciennes données
        collection.insert_many(data)
        print(f"✅ {len(data)} streamers du Top 500 mondial insérés dans MongoDB")
    except Exception as e:
        print(f"❌ Erreur MongoDB: Impossible de se connecter à la base de données")
        print(f"💡 Solution: Démarrez MongoDB avec la commande 'mongod' dans un autre terminal")
        print(f"🔧 Ou installez MongoDB: https://www.mongodb.com/try/download/community")

def insert_individual_profiles_data(data):
    """Insérer les données des profils individuels dans MongoDB"""
    try:
        collection = db["individual_profiles"]
        collection.delete_many({})  # Efface les anciennes données
        collection.insert_many(data)
        print(f"✅ {len(data)} profils individuels insérés dans MongoDB")
    except Exception as e:
        print(f"❌ Erreur MongoDB: Impossible de se connecter à la base de données")
        print(f"💡 Solution: Démarrez MongoDB avec la commande 'mongod' dans un autre terminal")
        print(f"🔧 Ou installez MongoDB: https://www.mongodb.com/try/download/community")
    collection = db["viewership_fr"]
    collection.delete_many({})
    collection.insert_many(data)

def insert_profiles_data(data):
    """
    Insère les données de profils détaillés dans MongoDB
    """
    collection = db["streamers_profiles_fr"]

    # Supprime les anciennes données
    collection.delete_many({})

    # Insère les nouvelles données
    if data:
        collection.insert_many(data)
        print(f"✅ {len(data)} profils insérés dans la collection 'streamers_profiles_fr'")
    else:
        print("⚠️ Aucune donnée de profil à insérer")
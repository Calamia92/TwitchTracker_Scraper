from db.mongo_client import db

def insert_viewership_data(data):
    collection = db["viewership_fr"]
    collection.delete_many({})
    collection.insert_many(data)
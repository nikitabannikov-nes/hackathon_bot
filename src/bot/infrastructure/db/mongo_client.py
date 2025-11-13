from pymongo import MongoClient

class MongoDB:
    def __init__(self, connection_string: str = "mongodb://localhost:27017/", db_name: str = "cleaning_app"):
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
    
    def close(self):
        self.client.close()

mongo_db = MongoDB()
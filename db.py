from pymongo import MongoClient

def start_db():
    dev_env = "mongodb+srv://ramonsa:capstone@capstone.pumy6yl.mongodb.net/?retryWrites=true&w=majority"
    prod = "mongodb+srv://admin:Password123@cs467.mvuciht.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(prod)
    db = client.get_database('Database0')
    jobs = db.jobs



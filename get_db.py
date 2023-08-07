# followed this tutorial for connecting to database: https://www.mongodb.com/languages/python
# certifi required because was getting connection issues
from pymongo import MongoClient
import certifi

def get_database():
    """
    Method to connect to our MongoDB.
    """
    client = MongoClient("mongodb+srv://ramonsa:capstone@capstone.pumy6yl.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=certifi.where())
    
    return client['users']

if __name__ == '__main__':
    db = get_database()
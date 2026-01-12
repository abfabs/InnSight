#!/usr/bin/env python3

from pymongo import MongoClient
import os

MONGO_URI = os.getenv('MONGOURI', 'mongodb://localhost:27017')
client = MongoClient(MONGO_URI)
db = client['innsight_db']

# Drop entire DB
client.drop_database('innsight_db')
print("✅ innsight_db DROPPED")

# Close
client.close()

#!/usr/bin/env python3

from pymongo import MongoClient
from config import Config


def drop_database():
    client = MongoClient(Config.MONGO_URI)
    client.drop_database(Config.MONGO_DB)
    client.close()
    print(f"✅ {Config.MONGO_DB} DROPPED")


def main():
    drop_database()
    return True


if __name__ == "__main__":
    main()

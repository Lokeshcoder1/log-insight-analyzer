from pymongo import MongoClient
from parser import parse_log_file


MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "log_insight"
COLLECTION_NAME = "logs"


def get_collection():
    client = MongoClient(MONGO_URI)

    database = client[DATABASE_NAME]
    collection = database[COLLECTION_NAME]

    return client, collection


def load_logs():
    log_file = "data/raw/application.log"

    parsed_logs = parse_log_file(log_file)

    client, collection = get_collection()

    if parsed_logs:
        result = collection.insert_many(parsed_logs)
        print(f"Inserted {len(result.inserted_ids)} logs into MongoDB.")

    client.close()


if __name__ == "__main__":
    load_logs()
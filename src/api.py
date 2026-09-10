from fastapi import FastAPI
from pymongo import MongoClient
from src.analyzer import analyze_request

app = FastAPI(title="Log Insight Analyzer")

MONGO_URI = "mongodb://localhost:27017"

client = MongoClient(MONGO_URI)
db = client["log_insight"]
logs_collection = db["logs"]


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/logs")
def get_logs():
    logs = list(
        logs_collection.find(
            {},
            {"_id": 0}
        ).limit(20)
    )

    return {
        "count": len(logs),
        "logs": logs
    }

@app.get("/logs/errors")
def get_error_logs():
    logs=list(
        logs_collection.find({"log_level":"ERROR"},
                             {"_id":0}).limit(20)
    )

    return{
        "count":len(logs),
        "error logs":logs
    }
@app.get("/logs/slow")
def get_slow_logs():
    logs=list(
        logs_collection.find({"response_time":{"$gt":1000}},
                             {"_id":0}).limit(20)
    )
    return {
        "count":len(logs),
        "slow logs":logs
    }

@app.get("/logs/request/{request_id}")
def get_request_logs(request_id: str):
    logs = list(
        logs_collection.find(
            {"request_id": request_id},
            {"_id": 0}
        )
    )

    return {
        "request_id": request_id,
        "count": len(logs),
        "logs": logs
    }

@app.get("/logs/request/{request_id}/analysis")
def analyze_request_logs(request_id:str):
    logs=list(logs_collection.find({"request_id":request_id},
                              {"_id":0}))
    analysis=analyze_request(logs)
    return{
        "request_id":request_id,
        "timeline"
        "":logs,
        "analysis":analysis
    }
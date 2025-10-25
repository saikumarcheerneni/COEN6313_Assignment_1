import os
import json
import requests
import redis
from dotenv import load_dotenv

#1 -->Loading environment variables from .env
load_dotenv()

#2 -->Connecting to Redis Cloud
print("Connecting to Redis Cloud...")

r = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    username=os.getenv("REDIS_USER"),
    password=os.getenv("REDIS_PASSWORD"),
    ssl=False,
    decode_responses=True
)

#3 --> Testing the connection
try:
    if r.ping():
        print(" Successfully connected to Redis Cloud!")
except Exception as e:
    print(" Redis connection failed:", e)
    exit(1)

#4 -->Fetching Nobel Prize dataset (2013–2023)
print("Downloading Nobel Prize dataset...")
URL = "https://api.nobelprize.org/v1/prize.json"
resp = requests.get(URL, timeout=30)
resp.raise_for_status()
data = resp.json()["prizes"]


filtered = [p for p in data if p.get("year") and 2013 <= int(p["year"]) <= 2023]
print(f" Found {len(filtered)} prize records between 2013–2023.")

for i, p in enumerate(filtered):
    key = f"prize:{p['year']}:{p['category']}:{i}"
    r.execute_command("JSON.SET", key, "$", json.dumps(p))

print(f" Successfully loaded {len(filtered)} Nobel prize entries into Redis Cloud!")

# import os
# import json
# import requests
# import redis
# from dotenv import load_dotenv

# # -------------------------------------------------------------
# # 1️⃣ Load environment variables
# # -------------------------------------------------------------
# load_dotenv()

# REDIS_HOST = os.getenv("REDIS_HOST")
# REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
# REDIS_USER = os.getenv("REDIS_USER", "default")
# REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
# USE_TLS = os.getenv("USE_TLS", "True").lower() == "false"

# # -------------------------------------------------------------
# # 2️⃣ Connect to Redis Cloud
# # -------------------------------------------------------------
# r = redis.Redis(
#     host=REDIS_HOST,
#     port=REDIS_PORT,
#     username=REDIS_USER,
#     password=REDIS_PASSWORD,
#     ssl=False,
#     decode_responses=True,
#     socket_timeout=15
# )

# try:
#     r.ping()
#     print(f"✅ Connected to Redis Cloud at {REDIS_HOST}:{REDIS_PORT}")
# except Exception as e:
#     print("❌ Redis connection failed:", e)
#     raise SystemExit

# # -------------------------------------------------------------
# # 3️⃣ Download Nobel Prize dataset
# # -------------------------------------------------------------
# URL = "https://api.nobelprize.org/v1/prize.json"
# print("🌐 Downloading Nobel Prize data…")
# resp = requests.get(URL, timeout=30)
# resp.raise_for_status()
# all_prizes = resp.json()["prizes"]

# # -------------------------------------------------------------
# # 4️⃣ Filter 2013–2023
# # -------------------------------------------------------------
# filtered = [p for p in all_prizes if p.get("year") and 2013 <= int(p["year"]) <= 2023]
# print(f"📘 Filtered {len(filtered)} prize records between 2013–2023.")

# # -------------------------------------------------------------
# # 5️⃣ Store each prize as JSON in Redis
# # -------------------------------------------------------------
# pipe = r.pipeline()
# for i, prize in enumerate(filtered, start=1):
#     year = int(prize["year"])
#     category = prize.get("category", "unknown")
#     laureates = prize.get("laureates", [])
#     doc = {"year": year, "category": category, "laureates": laureates}
#     key = f"prize:{year}:{category}:{i}"
#     pipe.execute_command("JSON.SET", key, "$", json.dumps(doc))
#     if i % 50 == 0:
#         pipe.execute()        # flush every 50
# pipe.execute()
# print(f"✅ Loaded {len(filtered)} prize documents into Redis Cloud.")

# # -------------------------------------------------------------
# # 6️⃣ Quick sanity-check
# # -------------------------------------------------------------
# sample_keys = r.keys("prize:2013:*")
# if sample_keys:
#     print(f"🔍 Sample key → {sample_keys[0]}")
#     print(json.dumps(r.json().get(sample_keys[0]), indent=2)[:400], "...\n")
# else:
#     print("⚠️ No keys found — check load process.")

# print("🎉 Data load complete for Nobel Prize dataset (2013–2023).")



import os
import json
import requests
import redis
from dotenv import load_dotenv

#1 -->Load environment variables from .env
load_dotenv()

#2 -->Connect to Redis Cloud
print("Connecting to Redis Cloud...")

r = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    username=os.getenv("REDIS_USER"),
    password=os.getenv("REDIS_PASSWORD"),
    ssl=False,
    decode_responses=True
)

#3 --> Test the connection
try:
    if r.ping():
        print(" Successfully connected to Redis Cloud!")
except Exception as e:
    print(" Redis connection failed:", e)
    exit(1)

#4 -->Fetch Nobel Prize dataset (2013–2023)
print("Downloading Nobel Prize dataset...")
URL = "https://api.nobelprize.org/v1/prize.json"
resp = requests.get(URL, timeout=30)
resp.raise_for_status()
data = resp.json()["prizes"]

# Filter only years 2013–2023
filtered = [p for p in data if p.get("year") and 2013 <= int(p["year"]) <= 2023]
print(f" Found {len(filtered)} prize records between 2013–2023.")

#5 -->Store data as JSON in Redis
for i, p in enumerate(filtered):
    key = f"prize:{p['year']}:{p['category']}:{i}"
    r.execute_command("JSON.SET", key, "$", json.dumps(p))

print(f" Successfully loaded {len(filtered)} Nobel prize entries into Redis Cloud!")

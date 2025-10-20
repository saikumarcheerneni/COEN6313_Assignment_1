# import os
# import redis
# from dotenv import load_dotenv
# import json

# # -------------------------------------------------------------
# # 1️⃣ Load environment variables
# # -------------------------------------------------------------
# load_dotenv()

# REDIS_HOST = os.getenv("REDIS_HOST")
# REDIS_PORT = int(os.getenv("REDIS_PORT"))
# REDIS_USER = os.getenv("REDIS_USER")
# REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
# USE_TLS = os.getenv("USE_TLS", "False").lower() == "false"

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
#     print(f"✅ Connected to Redis Cloud at {REDIS_HOST}:{REDIS_PORT}\n")
# except Exception as e:
#     print("❌ Redis connection failed:", e)
#     raise SystemExit

# # -------------------------------------------------------------
# # 3️⃣ Query functions
# # -------------------------------------------------------------
# def list_keys_by_pattern(pattern):
#     """List all keys matching a Redis pattern."""
#     keys = r.keys(pattern)
#     return keys

# def get_json(key):
#     """Fetch JSON document for a given key."""
#     data = r.execute_command("JSON.GET", key)
#     if data:
#         return json.loads(data)
#     return None

# def query_by_year(year):
#     print(f"🔹 Prizes for year {year}:")
#     keys = list_keys_by_pattern(f"prize:{year}:*")
#     if not keys:
#         print("No prizes found.\n")
#         return
#     for key in keys:
#         print(f"Key: {key}")
#         print(json.dumps(get_json(key), indent=2))
#     print("\n")

# def query_by_category(category):
#     print(f"🔹 Prizes in category '{category}':")
#     keys = list_keys_by_pattern(f"prize:*:{category}:*")
#     if not keys:
#         print("No prizes found.\n")
#         return
#     for key in keys:
#         print(f"Key: {key}")
#         print(json.dumps(get_json(key), indent=2))
#     print("\n")

# # -------------------------------------------------------------
# # 4️⃣ Example usage
# # -------------------------------------------------------------
# # List all keys (optional)
# # all_keys = list_keys_by_pattern("prize:*")
# # print("All prize keys:", all_keys, "\n")

# # Query by year
# query_by_year(2013)

# # Query by category
# query_by_category("physics")



import os
import json
import redis
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to Redis
r = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    username=os.getenv("REDIS_USER"),
    password=os.getenv("REDIS_PASSWORD"),
    ssl=False,
    decode_responses=True
)

def extract_json(doc_fields):
    """Extract and parse JSON content safely from FT.SEARCH result fields."""
    if not doc_fields or len(doc_fields) < 2:
        return None
    # Find the field containing JSON (usually at index 1 or "$")
    for j in range(1, len(doc_fields), 2):
        val = doc_fields[j]
        if val and val.strip() and val.strip()[0] in ['{', '[']:
            try:
                return json.loads(val)
            except Exception:
                pass
    return None

def laureate_count_by_category(category, start, end):
    q = f'@category:{{{category}}} @year:[{start} {end}]'
    res = r.execute_command("FT.SEARCH", "idx:prizes", q, "RETURN", "1", "$")
    total = 0

    if res[0] == 0:
        print(f" No results for {category} between {start}-{end}.")
        return

    # Safe iteration over the field entries
    for fields in res[2::2]:  # start at index 2, step by 2
        doc = extract_json(fields)
        if doc and "laureates" in doc:
            total += len(doc["laureates"])

    print(f" Total laureates in {category} ({start}-{end}): {total}")

def laureate_count_by_keyword(keyword):
    q = f'@motivation:{keyword}'
    res = r.execute_command("FT.SEARCH", "idx:prizes", q, "RETURN", "1", "$")
    total = 0

    if res[0] == 0:
        print(f" No results found for keyword '{keyword}'.")
        return

    for fields in res[2::2]:
        doc = extract_json(fields)
        if doc and "laureates" in doc:
            total += len(doc["laureates"])

    print(f" Laureates with keyword '{keyword}': {total}")

def find_laureate(first, last):
    q = f'@firstname:({first}) @lastname:({last})'
    res = r.execute_command("FT.SEARCH", "idx:prizes", q, "RETURN", "1", "$")

    if res[0] == 0:
        print(f" No laureate found for {first} {last}.")
        return

    for fields in res[2::2]:
        doc = extract_json(fields)
        if not doc:
            continue
        year = str(doc.get("year", "?"))
        category = doc.get("category", "?")
        for l in doc.get("laureates", []):
            if l["firstname"].lower() == first.lower() and l["surname"].lower() == last.lower():
                print(f"🏅 {l['firstname']} {l['surname']} — {year} ({category})")
                print(f"   Motivation: {l['motivation']}")

# Example test calls
if __name__ == "__main__":
    laureate_count_by_category("physics", 2013, 2023)
    laureate_count_by_keyword("quantum")
    find_laureate("Peter", "Higgs")

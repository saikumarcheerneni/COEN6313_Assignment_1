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


    for fields in res[2::2]:  
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

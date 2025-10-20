import os
import redis
from dotenv import load_dotenv

load_dotenv()

r = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    username=os.getenv("REDIS_USER"),
    password=os.getenv("REDIS_PASSWORD"),
    ssl=False,
    decode_responses=True
)

try:
    r.execute_command(
        "FT.CREATE", "idx:prizes", "ON", "JSON",
        "PREFIX", "1", "prize:",
        "SCHEMA",
        "$.year", "AS", "year", "NUMERIC", "SORTABLE",
        "$.category", "AS", "category", "TAG", "SORTABLE",
        "$.laureates[*].firstname", "AS", "firstname", "TEXT",
        "$.laureates[*].surname", "AS", "lastname", "TEXT",
        "$.laureates[*].motivation", "AS", "motivation", "TEXT"
    )
    print(" Index created successfully (with NUMERIC year).")
except redis.exceptions.ResponseError as e:
    print("ℹ ", e)

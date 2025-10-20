import redis

# --------------------------------------------
#  Test connection to Redis Cloud (non-TLS)
# --------------------------------------------
r = redis.Redis(
    host="redis-17778.c10.us-east-1-3.ec2.redns.redis-cloud.com",
    port=17778,
    username="Saikumar",
    password="Raja@12345",
    ssl=False  #  must be False for your free-tier database
)

try:
    r.ping()
    print(" Connected to Redis Cloud successfully (non-TLS)!")
except Exception as e:
    print(" Redis connection failed:", e)
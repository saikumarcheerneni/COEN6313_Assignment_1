import redis

# --------------------------------------------
#  Test connection to Redis Cloud
# --------------------------------------------
r = redis.Redis(
    host="redis-17778.c10.us-east-1-3.ec2.redns.redis-cloud.com",
    port=17778,
    username="Saikumar",
    password="Raja@12345",
    ssl=False 
)

try:
    r.ping()
    print(" Connected to Redis Cloud successfully (non-TLS)!")
except Exception as e:
    print(" Redis connection failed:", e)
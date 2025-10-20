import os
import json
import grpc
import redis
from concurrent import futures
from dotenv import load_dotenv

import proto.nobel_pb2 as nobel_pb2
import proto.nobel_pb2_grpc as nobel_pb2_grpc


# ==========================================================
# 1️⃣ Connect to Redis Cloud using .env credentials
# ==========================================================
load_dotenv()

r = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    username=os.getenv("REDIS_USER"),
    password=os.getenv("REDIS_PASSWORD"),
    ssl=False,  # For Redis Cloud free-tier (non-TLS)
    socket_timeout=15
)

INDEX = "nobel_index"


# ==========================================================
# 2️⃣ Define gRPC Service Implementation
# ==========================================================
class NobelService(nobel_pb2_grpc.NobelQueryServicer):

    # ------------------------------------------------------
    # Count prizes per category in a year range
    # ------------------------------------------------------
    def CountByCategory(self, request, context):
        try:
            q = f'@category:{{{request.category}}} @year:[{request.year_start} {request.year_end}]'

            res = r.execute_command(
                "FT.AGGREGATE", INDEX, q,
                "GROUPBY", "1", "@category",
                "REDUCE", "COUNT", "0", "AS", "num_prizes"
            )

            print(f"🔍 Aggregation result for {request.category}: {res}")

            count = 0
            if isinstance(res, (list, tuple)) and len(res) > 1:
                try:
                    raw_value = res[1][1] if len(res[1]) > 1 else 0
                    if isinstance(raw_value, bytes):
                        raw_value = raw_value.decode("utf-8")
                    count = int(raw_value) if str(raw_value).isdigit() else 0
                except Exception:
                    count = 0

            return nobel_pb2.CountResponse(total=count)

        except Exception as e:
            print(f"⚠️ Error in CountByCategory: {e}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return nobel_pb2.CountResponse(total=0)

    # ------------------------------------------------------
    # Count prizes for a specific year
    # ------------------------------------------------------
    def CountByYear(self, request, context):
        try:
            q = f'@year:[{request.year} {request.year}]'
            res = r.execute_command(
                "FT.AGGREGATE", INDEX, q,
                "GROUPBY", "1", "@year",
                "REDUCE", "COUNT", "0", "AS", "num_prizes"
            )

            print(f"📅 Aggregation result for year {request.year}: {res}")

            count = 0
            if isinstance(res, (list, tuple)) and len(res) > 1:
                try:
                    raw_value = res[1][1] if len(res[1]) > 1 else 0
                    if isinstance(raw_value, bytes):
                        raw_value = raw_value.decode("utf-8")
                    count = int(raw_value) if str(raw_value).isdigit() else 0
                except Exception:
                    count = 0

            return nobel_pb2.CountResponse(total=count)

        except Exception as e:
            print(f"⚠️ Error in CountByYear: {e}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return nobel_pb2.CountResponse(total=0)

    # ------------------------------------------------------
    # ✅ FIXED Search laureates by firstname
    # ------------------------------------------------------
    def SearchByFirstname(self, request, context):
        try:
            # ✅ Correct RediSearch 2.x / Redis 8 syntax for JSON search
            q = f'@firstname:{{{request.firstname}*}}'

            res = r.execute_command(
                "FT.SEARCH", INDEX, q,
                "RETURN", "4",
                "$.year", "$.category",
                "$.laureates[*].firstname", "$.laureates[*].surname"
            )

            hits = []

            # Redis returns [total, key1, json1, key2, json2, ...]
            for i in range(2, len(res), 2):
                raw_doc = res[i]
                if isinstance(raw_doc, bytes):
                    raw_doc = raw_doc.decode("utf-8")

                doc = json.loads(raw_doc)

                # Year
                year_val = doc.get("year", "")
                if isinstance(year_val, bytes):
                    year_val = year_val.decode("utf-8")
                year_int = int(year_val) if str(year_val).isdigit() else 0

                # Category
                category_val = doc.get("category", "")
                if isinstance(category_val, bytes):
                    category_val = category_val.decode("utf-8")

                # Laureates array
                laureates = doc.get("laureates", [])
                for l in laureates:
                    firstname = str(l.get("firstname", ""))
                    surname = str(l.get("surname", ""))
                    if firstname.lower().startswith(request.firstname.lower()):
                        hits.append(
                            nobel_pb2.Hit(
                                year=year_int,
                                category=str(category_val),
                                firstname=firstname,
                                surname=surname
                            )
                        )

            print(f"✅ Found {len(hits)} laureates for firstname '{request.firstname}'")
            return nobel_pb2.SearchResults(hits=hits)

        except Exception as e:
            print("⚠️ Error in SearchByFirstname:", e)
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return nobel_pb2.SearchResults(hits=[])


# ==========================================================
# 3️⃣ Start gRPC Server
# ==========================================================
def serve():
    try:
        r.ping()
        print("✅ Connected to Redis Cloud successfully (non-TLS)!")
    except Exception as e:
        print("❌ Redis connection failed:", e)
        return

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    nobel_pb2_grpc.add_NobelQueryServicer_to_server(NobelService(), server)

    server.add_insecure_port("[::]:50051")
    print("🚀 gRPC server running on port 50051")

    server.start()
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped manually.")


# ==========================================================
# 4️⃣ Entry point
# ==========================================================
if __name__ == "__main__":
    serve()
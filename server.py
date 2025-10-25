import os, json, redis, grpc
from concurrent import futures
from dotenv import load_dotenv
import proto.noble_pb2 as noble_pb2
import proto.noble_pb2_grpc as noble_pb2_grpc

load_dotenv()

r = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    username=os.getenv("REDIS_USER"),
    password=os.getenv("REDIS_PASSWORD"),
    ssl=False,
    decode_responses=True
)

def safe_load(doc_fields):
    if not doc_fields or len(doc_fields) < 2:
        return None
    val = doc_fields[1]  
    try:
        return json.loads(val)
    except Exception:
        return None

class NobelServiceServicer(noble_pb2_grpc.NobelServiceServicer):

    def GetLaureateCountByCategoryRange(self, request, context):
        q = f"@category:{{{request.category}}} @year:[{request.start_year} {request.end_year}]"
        res = r.execute_command("FT.SEARCH", "idx:prizes", q, "RETURN", "1", "$")
        count = 0
        for fields in res[2::2]:
            data = safe_load(fields)
            if data and "laureates" in data:
                count += len(data["laureates"])
        return noble_pb2.CountReply(count=count)

    def GetLaureateCountByMotivationKeyword(self, request, context):
        q = f"@motivation:{request.keyword}"
        res = r.execute_command("FT.SEARCH", "idx:prizes", q, "RETURN", "1", "$")
        count = 0
        for fields in res[2::2]:
            data = safe_load(fields)
            if data and "laureates" in data:
                count += len(data["laureates"])
        return noble_pb2.CountReply(count=count)

    def FindLaureateByName(self, request, context):
        q = f"@firstname:({request.firstname}) @lastname:({request.lastname})"
        res = r.execute_command("FT.SEARCH", "idx:prizes", q, "RETURN", "1", "$")
        laureates = []
        for fields in res[2::2]:
            data = safe_load(fields)
            if not data or "laureates" not in data:
                continue
            year, category = str(data.get("year", "?")), data.get("category", "?")
            for la in data["laureates"]:
                if la["firstname"].lower() == request.firstname.lower() and la["surname"].lower() == request.lastname.lower():
                    laureates.append(
                        noble_pb2.LaureateRecord(
                            firstname=la["firstname"],
                            lastname=la["surname"],
                            year=year,
                            category=category,
                            motivation=la["motivation"]
                        )
                    )
        return noble_pb2.LaureateReply(laureates=laureates)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    noble_pb2_grpc.add_NobelServiceServicer_to_server(NobelServiceServicer(), server)
    server.add_insecure_port('0.0.0.0:55001')
    server.start()
    print("gRPC server running on port 55001...")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()

import grpc
from proto import noble_pb2, noble_pb2_grpc
import time
import matplotlib.pyplot as plt

# Replace with your Azure VM public IP
VM_IP = "57.154.70.62"
PORT = 55001
NUM_RUNS = 1000

def measure_delays(stub, query_type, n=NUM_RUNS):
    delays = []
    for _ in range(n):
        start = time.time()
        try:
            if query_type == "category":
                stub.GetLaureateCountByCategoryRange(
                    noble_pb2.CategoryRangeRequest(category="Physics", start_year=2013, end_year=2023)
                )
            elif query_type == "keyword":
                stub.GetLaureateCountByMotivationKeyword(
                    noble_pb2.KeywordRequest(keyword="Quantum")
                )
            elif query_type == "name":
                stub.FindLaureateByName(
                    noble_pb2.NameRequest(firstname="Peter", lastname="Higgs")
                )
        except grpc.RpcError as e:
            print(f"RPC failed for {query_type}: {e}")
            delays.append(None)
            continue
        end = time.time()
        delays.append(end - start)
    # Filter out failed attempts
    return [d for d in delays if d is not None]

def run():
    with grpc.insecure_channel(f"{VM_IP}:{PORT}") as channel:
        stub = noble_pb2_grpc.NobelServiceStub(channel)

        print("\nMeasuring delays for Category query...")
        delays_category = measure_delays(stub, "category")
        print(f"Category query delays (first 5 runs): {delays_category[:5]}")

        print("\nMeasuring delays for Keyword query...")
        delays_keyword = measure_delays(stub, "keyword")
        print(f"Keyword query delays (first 5 runs): {delays_keyword[:5]}")

        print("\nMeasuring delays for Name query...")
        delays_name = measure_delays(stub, "name")
        print(f"Name query delays (first 5 runs): {delays_name[:5]}")

        # Plot boxplots
        plt.boxplot([delays_category, delays_keyword, delays_name], labels=["Category", "Keyword", "Name"])
        plt.ylabel("End-to-End Delay (seconds)")
        plt.title(f"gRPC Query Delays ({NUM_RUNS} runs)")
        plt.show()

        # Print averages
        print(f"\nAverage delays:")
        print(f"Category: {sum(delays_category)/len(delays_category):.4f}s")
        print(f"Keyword: {sum(delays_keyword)/len(delays_keyword):.4f}s")
        print(f"Name: {sum(delays_name)/len(delays_name):.4f}s")

if __name__ == "__main__":
    run()

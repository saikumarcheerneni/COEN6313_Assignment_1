# import grpc
# from proto import noble_pb2, noble_pb2_grpc
# import time
# import matplotlib.pyplot as plt
# import seaborn as sns
# import pandas as pd
# from matplotlib.ticker import MaxNLocator

# # Replace with your Azure VM public IP
# VM_IP = "57.154.70.62"
# PORT = 55001
# NUM_RUNS = 100


# def measure_delays(stub, query_type, n=NUM_RUNS):

#     delays = []
#     for _ in range(n):
#         start = time.time()
#         try:
#             if query_type == "category":
#                 stub.GetLaureateCountByCategoryRange(
#                     noble_pb2.CategoryRangeRequest(category="Physics", start_year=2013, end_year=2023)
#                 )
#             elif query_type == "keyword":
#                 stub.GetLaureateCountByMotivationKeyword(
#                     noble_pb2.KeywordRequest(keyword="Quantum")
#                 )
#             elif query_type == "name":
#                 stub.FindLaureateByName(
#                     noble_pb2.NameRequest(firstname="Peter", lastname="Higgs")
#                 )
#         except grpc.RpcError as e:
#             print(f"RPC failed for {query_type}: {e}")
#             delays.append(None)
#             continue
#         end = time.time()
#         delays.append(end - start)

#     return [d for d in delays if d is not None]


# def run():
#     with grpc.insecure_channel(f"{VM_IP}:{PORT}") as channel:
#         stub = noble_pb2_grpc.NobelServiceStub(channel)

#         print("\nMeasuring delays for Category query...")
#         delays_category = measure_delays(stub, "category")

#         print("\nMeasuring delays for Keyword query...")
#         delays_keyword = measure_delays(stub, "keyword")

#         print("\nMeasuring delays for Name query...")
#         delays_name = measure_delays(stub, "name")

#         all_data = pd.DataFrame({
#             "Category": delays_category,
#             "Keyword": delays_keyword,
#             "Name": delays_name
#         })
#         melted = all_data.melt(var_name="Query Type", value_name="Delay (s)")
#         sns.set_theme(style="white", context="talk")
#         plt.figure(figsize=(8, 6), facecolor="#f8f9fa")
#         palette = sns.color_palette(["#88CCEE", "#DDCC77", "#CC6677"])
#         ax = sns.violinplot(
#             data=melted,
#             x="Query Type",
#             y="Delay (s)",
#             inner="quartile",
#             linewidth=1.2,
#             palette=palette,
#             alpha=0.85
#         )

#         plt.title(f"gRPC Query Delay Distributions ({NUM_RUNS} runs)",
#                   fontsize=15, fontweight="bold", pad=15, color="#222831")
#         plt.ylabel("End-to-End Delay (seconds)", fontsize=12, color="#222831")
#         plt.xlabel("Query Type", fontsize=12, color="#222831")

#         ax.set_facecolor("#ffffff")
#         plt.grid(axis="y", linestyle="--", alpha=0.5)
#         ax.spines['top'].set_visible(False)
#         ax.spines['right'].set_visible(False)
#         ax.yaxis.set_major_locator(MaxNLocator(nbins=8))

#         for i, box in enumerate(["Category", "Keyword", "Name"]):
#             y_median = melted[melted["Query Type"] == box]["Delay (s)"].median()
#             ax.text(i, y_median + 0.005, f"Median: {y_median:.2f}s",
#                     ha='center', va='bottom', fontsize=10, color="#222831", fontweight='semibold')

#         plt.tight_layout()
#         plt.savefig("grpc_violin_clean.png", dpi=300, bbox_inches='tight', facecolor="#f8f9fa")
#         plt.show()

#         print("\nAverage and Std Dev of Delays:")
#         for query_type, delays in zip(["Category", "Keyword", "Name"],
#                                       [delays_category, delays_keyword, delays_name]):
#             print(f"{query_type:<10}: mean={sum(delays)/len(delays):.4f}s, std={pd.Series(delays).std():.4f}s")

#         print("\n Figure saved as grpc_violin_clean.png")


# if __name__ == "__main__":
#     run()

import grpc
from proto import noble_pb2, noble_pb2_grpc
import time
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from matplotlib.ticker import MaxNLocator
import warnings


warnings.filterwarnings("ignore", category=FutureWarning)

VM_IP = "57.154.70.62"
PORT = 55001
NUM_RUNS = 100


def measure_delays(stub, query_type, params, n=NUM_RUNS):
    """Measure end-to-end delays for given query type."""
    delays = []
    for _ in range(n):
        start = time.time()
        try:
            if query_type == "category":
                stub.GetLaureateCountByCategoryRange(
                    noble_pb2.CategoryRangeRequest(
                        category=params["category"],
                        start_year=params["start_year"],
                        end_year=params["end_year"]
                    )
                )
            elif query_type == "keyword":
                stub.GetLaureateCountByMotivationKeyword(
                    noble_pb2.KeywordRequest(keyword=params["keyword"])
                )
            elif query_type == "name":
                stub.FindLaureateByName(
                    noble_pb2.NameRequest(
                        firstname=params["firstname"],
                        lastname=params["lastname"]
                    )
                )
        except grpc.RpcError as e:
            print(f" RPC failed for {query_type}: {e}")
            continue
        end = time.time()
        delays.append(end - start)
    return delays


def run():
    with grpc.insecure_channel(f"{VM_IP}:{PORT}") as channel:
        stub = noble_pb2_grpc.NobelServiceStub(channel)

        print("\n Measuring delays for three gRPC queries...\n")

        # Collect inputs ONCE
        category = input("Enter category (e.g., Physics): ")
        start_year = int(input("Enter start year (e.g., 2013): "))
        end_year = int(input("Enter end year (e.g., 2023): "))
        keyword = input("Enter keyword (e.g., Quantum): ")
        firstname = input("Enter laureate first name (e.g., Peter): ")
        lastname = input("Enter laureate last name (e.g., Higgs): ")

        print("\n Running 100 measurements each...\n")

        delays_category = measure_delays(stub, "category", {
            "category": category, "start_year": start_year, "end_year": end_year})
        delays_keyword = measure_delays(stub, "keyword", {"keyword": keyword})
        delays_name = measure_delays(stub, "name", {
            "firstname": firstname, "lastname": lastname})

   
        for query, delays in [
            ("Category", delays_category),
            ("Keyword", delays_keyword),
            ("Name", delays_name),
        ]:
            mean = sum(delays) / len(delays)
            std = pd.Series(delays).std()
            print(f"{query:<10}: mean={mean:.4f}s | std={std:.4f}s | min={min(delays):.4f}s | max={max(delays):.4f}s")

        all_data = pd.DataFrame({
            "Category": delays_category,
            "Keyword": delays_keyword,
            "Name": delays_name
        })
        melted = all_data.melt(var_name="Query Type", value_name="Delay (s)")

        sns.set_theme(style="white", context="talk")
        plt.figure(figsize=(8, 6), facecolor="#f8f9fa")
        palette = sns.color_palette(["#88CCEE", "#DDCC77", "#CC6677"])

        ax = sns.violinplot(
            data=melted,
            x="Query Type",
            y="Delay (s)",
            inner=None,
            linewidth=1.2,
            palette=palette
        )

        plt.title(f"gRPC Query Delay Distributions ({NUM_RUNS} runs)",
                  fontsize=15, fontweight="bold", pad=15, color="#222831")
        plt.ylabel("End-to-End Delay (seconds)", fontsize=12, color="#222831")
        plt.xlabel("Query Type", fontsize=12, color="#222831")

        ax.set_facecolor("#ffffff")
        plt.grid(axis="y", linestyle="--", alpha=0.5)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.yaxis.set_major_locator(MaxNLocator(nbins=8))

        for i, q in enumerate(["Category", "Keyword", "Name"]):
            y_median = melted[melted["Query Type"] == q]["Delay (s)"].median()
            ax.text(i, y_median + 0.005, f"Median: {y_median:.2f}s",
                    ha='center', va='bottom', fontsize=10, color="#222831", fontweight='semibold')

        plt.tight_layout()
        plt.savefig("grpc_violin_clean.png", dpi=300, bbox_inches='tight', facecolor="#f8f9fa")
        plt.show()

        print("\n Figure saved as grpc_violin_clean.png")


if __name__ == "__main__":
    run()

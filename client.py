# import grpc
# from proto import noble_pb2, noble_pb2_grpc
# import time
# import matplotlib.pyplot as plt

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
#     # Filter out failed attempts
#     return [d for d in delays if d is not None]

# def run():
#     with grpc.insecure_channel(f"{VM_IP}:{PORT}") as channel:
#         stub = noble_pb2_grpc.NobelServiceStub(channel)

#         print("\nMeasuring delays for Category query...")
#         delays_category = measure_delays(stub, "category")
#         print(f"Category query delays (first 5 runs): {delays_category[:5]}")

#         print("\nMeasuring delays for Keyword query...")
#         delays_keyword = measure_delays(stub, "keyword")
#         print(f"Keyword query delays (first 5 runs): {delays_keyword[:5]}")

#         print("\nMeasuring delays for Name query...")
#         delays_name = measure_delays(stub, "name")
#         print(f"Name query delays (first 5 runs): {delays_name[:5]}")

#         # Plot boxplots
#         plt.boxplot([delays_category, delays_keyword, delays_name], labels=["Category", "Keyword", "Name"])
#         plt.ylabel("End-to-End Delay (seconds)")
#         plt.title(f"gRPC Query Delays ({NUM_RUNS} runs)")
#         plt.show()

#         # Print averages
#         print(f"\nAverage delays:")
#         print(f"Category: {sum(delays_category)/len(delays_category):.4f}s")
#         print(f"Keyword: {sum(delays_keyword)/len(delays_keyword):.4f}s")
#         print(f"Name: {sum(delays_name)/len(delays_name):.4f}s")

# if __name__ == "__main__":
#     run()
# import seaborn as sns
# import pandas as pd
# import matplotlib.pyplot as plt
# from matplotlib.ticker import MaxNLocator

# # Combine data into a DataFrame
# all_data = pd.DataFrame({
#     "Category": delays_category,
#     "Keyword": delays_keyword,
#     "Name": delays_name
# })

# # Melt into long form for Seaborn
# melted = all_data.melt(var_name="Query Type", value_name="Delay (s)")

# # 🎨 --- Figure Beautification ---
# plt.style.use("seaborn-v0_8-whitegrid")
# sns.set_theme(style="whitegrid", context="talk")

# # Custom color palette (soft + professional)
# palette = sns.color_palette(["#A1C9F4", "#FFB482", "#8DE5A1"])

# # Create figure
# plt.figure(figsize=(8, 6))
# ax = sns.violinplot(
#     data=melted,
#     x="Query Type",
#     y="Delay (s)",
#     inner="quartile",
#     linewidth=1.3,
#     palette=palette,
#     alpha=0.9
# )

# # Overlay individual data points (adds realism)
# sns.stripplot(
#     data=melted,
#     x="Query Type",
#     y="Delay (s)",
#     color="black",
#     size=3,
#     jitter=0.25,
#     alpha=0.4
# )

# # 🏷️ Titles & labels
# plt.title(f"🎸 gRPC Query Delay Distributions ({NUM_RUNS} runs)",
#           fontsize=15, fontweight="bold", pad=15)
# plt.ylabel("End-to-End Delay (seconds)", fontsize=12)
# plt.xlabel("Query Type", fontsize=12)
# plt.grid(axis="y", linestyle="--", alpha=0.5)

# # Format y-axis for readability
# ax.yaxis.set_major_locator(MaxNLocator(nbins=8))
# ax.spines['top'].set_visible(False)
# ax.spines['right'].set_visible(False)

# # Annotate medians
# for i, box in enumerate(["Category", "Keyword", "Name"]):
#     y_median = melted[melted["Query Type"] == box]["Delay (s)"].median()
#     ax.text(i, y_median + 0.01, f"Median: {y_median:.2f}s",
#             ha='center', va='bottom', fontsize=10, color='black', fontweight='semibold')

# # Tight layout and save option
# plt.tight_layout()
# plt.savefig("grpc_violin_plot.png", dpi=300, bbox_inches='tight')
# plt.show()

# # 📊 Print statistics
# print("\n📊 Average and Std Dev of Delays:")
# for query_type, delays in zip(["Category", "Keyword", "Name"],
#                               [delays_category, delays_keyword, delays_name]):
#     print(f"{query_type:<10}: mean={sum(delays)/len(delays):.4f}s, std={pd.Series(delays).std():.4f}s")
# print("\n✅ Figure saved as grpc_violin_plot.png")


import grpc
from proto import noble_pb2, noble_pb2_grpc
import time
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from matplotlib.ticker import MaxNLocator

# Replace with your Azure VM public IP
VM_IP = "57.154.70.62"
PORT = 55001
NUM_RUNS = 100


def measure_delays(stub, query_type, n=NUM_RUNS):
    """Measure query delays for different query types."""
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

    # Remove failed attempts (None)
    return [d for d in delays if d is not None]


def run():
    with grpc.insecure_channel(f"{VM_IP}:{PORT}") as channel:
        stub = noble_pb2_grpc.NobelServiceStub(channel)

        print("\nMeasuring delays for Category query...")
        delays_category = measure_delays(stub, "category")

        print("\nMeasuring delays for Keyword query...")
        delays_keyword = measure_delays(stub, "keyword")

        print("\nMeasuring delays for Name query...")
        delays_name = measure_delays(stub, "name")

        # --- 🎨 Visualization (Seaborn Violin Plot) ---
        all_data = pd.DataFrame({
            "Category": delays_category,
            "Keyword": delays_keyword,
            "Name": delays_name
        })
        melted = all_data.melt(var_name="Query Type", value_name="Delay (s)")

        # Use clean theme
        sns.set_theme(style="white", context="talk")

        # Soft background
        plt.figure(figsize=(8, 6), facecolor="#f8f9fa")

        # Gentle pastel colors
        palette = sns.color_palette(["#88CCEE", "#DDCC77", "#CC6677"])

        # Draw violin plot (no dots)
        ax = sns.violinplot(
            data=melted,
            x="Query Type",
            y="Delay (s)",
            inner="quartile",
            linewidth=1.2,
            palette=palette,
            alpha=0.85
        )

        # Titles & labels
        plt.title(f"🎸 gRPC Query Delay Distributions ({NUM_RUNS} runs)",
                  fontsize=15, fontweight="bold", pad=15, color="#222831")
        plt.ylabel("End-to-End Delay (seconds)", fontsize=12, color="#222831")
        plt.xlabel("Query Type", fontsize=12, color="#222831")

        # Grid & background styling
        ax.set_facecolor("#ffffff")
        plt.grid(axis="y", linestyle="--", alpha=0.5)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.yaxis.set_major_locator(MaxNLocator(nbins=8))

        # Median annotations
        for i, box in enumerate(["Category", "Keyword", "Name"]):
            y_median = melted[melted["Query Type"] == box]["Delay (s)"].median()
            ax.text(i, y_median + 0.005, f"Median: {y_median:.2f}s",
                    ha='center', va='bottom', fontsize=10, color="#222831", fontweight='semibold')

        # Save and show
        plt.tight_layout()
        plt.savefig("grpc_violin_clean.png", dpi=300, bbox_inches='tight', facecolor="#f8f9fa")
        plt.show()

        # 📊 Print statistics
        print("\n📊 Average and Std Dev of Delays:")
        for query_type, delays in zip(["Category", "Keyword", "Name"],
                                      [delays_category, delays_keyword, delays_name]):
            print(f"{query_type:<10}: mean={sum(delays)/len(delays):.4f}s, std={pd.Series(delays).std():.4f}s")

        print("\n✅ Figure saved as grpc_violin_clean.png")


if __name__ == "__main__":
    run()


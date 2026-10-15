from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def load_metrics_data(output_folder: str) -> pd.DataFrame:
    """Runs through all subfolders of the given base folder, finds all CSV files named 'metrics.csv', and concatenates them into a single DataFrame."""
    caminho_base = Path(output_folder)
    list_dataframes = []
    
    # Find all 'metrics.csv' files in the base folder and its subfolders
    for ficheiro_csv in caminho_base.rglob("metrics.csv"):
        try:
            df = pd.read_csv(ficheiro_csv)
            list_dataframes.append(df)
        except Exception as e:
            print(f"⚠️ Erro ao ler {ficheiro_csv}: {e}")
            
    if not list_dataframes:
        raise ValueError(f"Nenhum ficheiro metrics.csv encontrado na pasta '{output_folder}'.")
        
    # Joins all DataFrames into one
    return pd.concat(list_dataframes, ignore_index=True)

def generate_charts(output_folder: str) -> None:
    print("Loading Data...")
    df = load_metrics_data(output_folder)
    
    print(f"Total number of records loaded: {len(df)}")
    
    # Set the theme for seaborn plots
    sns.set_theme(style="whitegrid")
    
    # ---------------------------------------------------------
    # Graph 1: Boxplot (Execution Time Distribution)
    # This graph shows the distribution of execution times for each model, highlighting outliers and the median.
    # ---------------------------------------------------------
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df, x="Model", y="Elapsed Time (seconds)", hue="Model", palette="viridis")
    
    plt.title("Execution Time Distribution by Model", fontsize=16, pad=15)
    plt.xlabel("Model", fontsize=12)
    plt.ylabel("Time (Seconds)", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.yscale("log")
    plt.tight_layout()
    
    plt.savefig("graph_times_boxplot.png", dpi=300)
    print("✅ Boxplot graph saved as 'graph_times_boxplot.png'")
    
    # ---------------------------------------------------------
    # Graph 2: Bar Chart (Average Execution Time with Error Bars)
    # This graph shows the average execution time for each model, with error bars representing the standard deviation.
    # ---------------------------------------------------------
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df, x="Model", y="Elapsed Time (seconds)", hue="Model", palette="mako")
    
    plt.title("Average Execution Time by Model", fontsize=16, pad=15)
    plt.xlabel("Model", fontsize=12)
    plt.ylabel("Average Time (Seconds)", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    
    plt.savefig("graph_times_barchart.png", dpi=300)
    print("✅ Bar chart graph saved as 'graph_times_barchart.png'")
    
    #---------------------------------------------------------
    # Graph 3: Scatter Plot (Elapsed Time vs. Total Tokens)
    # This graph shows the relationship between the total number of tokens processed and the elapsed time for each model. A regression line is added to visualize the trend.
    # ---------------------------------------------------------
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x="Total Tokens", y="Elapsed Time (seconds)", hue="Model", alpha=0.6)
    sns.regplot(data=df, x="Total Tokens", y="Elapsed Time (seconds)", scatter=False, color="black", logx=True)
    plt.title("Elapsed Time vs. Total Tokens by Model", fontsize=16, pad=15)
    plt.xlabel("Total Tokens", fontsize=12)
    plt.ylabel("Elapsed Time (seconds)", fontsize=12)
    plt.tight_layout()
    
    plt.savefig("graph_times_scatter.png", dpi=300)
    print("✅ Scatter plot graph saved as 'graph_times_scatter.png'")

    # ---------------------------------------------------------
    # Graph 4: Throughput (Tokens per Second)
    # This graph shows the throughput of each model in terms of tokens processed per second.
    # ---------------------------------------------------------
    df["Tokens/Sec"] = df["Response Tokens"] / df["Elapsed Time (seconds)"]
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df, x="Model", y="Tokens/Sec", hue="Model", palette="rocket")
    plt.title("Throughput (Tokens per Second) by Model", fontsize=16, pad=15)
    plt.xlabel("Modelos")
    plt.ylabel("Tokens/Seg")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    
    plt.savefig("graph_throughput_barchart.png", dpi=300)
    print("✅ Throughput bar chart graph saved as 'graph_throughput_barchart.png'")
    
    # ---------------------------------------------------------
    # Graph 5: CDF (Cumulative Distribution Function) of Execution Times
    # This graph shows the cumulative distribution of execution times for each model, allowing for a comparison of performance across models.
    # ---------------------------------------------------------
    plt.figure(figsize=(10, 6))
    sns.ecdfplot(data=df, x="Elapsed Time (seconds)", hue="Model", linewidth=2)
    plt.title("Cumulative Distribution of Execution Times by Model", fontsize=16, pad=15)
    plt.ylabel("Cumulative Probability", fontsize=12)
    plt.xlabel("Elapsed Time (Seconds)", fontsize=12)
    plt.xscale("log")
    plt.tight_layout()
    
    plt.savefig("graph_times_cdf.png", dpi=300)
    print("✅ CDF graph saved as 'graph_times_cdf.png'")
    
    plt.show()

def generate_summary_statistics(output_folder: str) -> pd.DataFrame:
    """Generates summary statistics (min, max, mean, median, std) for the metrics data and saves it to a CSV file."""
    df = load_metrics_data(output_folder)

    target_columns = [
        "Elapsed Time (seconds)",
        "Prompt Tokens",
        "Response Tokens",
        "Total Tokens",
    ]

    # Group by 'Model' and calculate summary statistics for the target columns
    stats_df = df.groupby("Model")[target_columns].agg(
        ["min", "max", "mean", "median", "std"]
    )

    stats_df = stats_df.round(3)

    # Save the summary statistics to a CSV file
    summary_csv_path = Path(output_folder) / "summary_statistics.csv"
    stats_df.to_csv(summary_csv_path)

    print(f"✅ Summary statistics saved to '{summary_csv_path}'\n")

    # Imprime no terminal de forma legível
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 1000)
    print("--- SUMMARY STATISTICS ---")
    print(stats_df)

    return stats_df

if __name__ == "__main__":
    generate_summary_statistics("trustdev-output")
import os
from tradebot import GeminiMarketAnalyzer
from trade import dataRetriever
from tradde import process_files_by_currency
from datetime import datetime
from forex_mailer import markdown_to_html_email
from price_channels import PriceChannelAnalyzer
import time
from threading import Lock
from concurrent.futures import ProcessPoolExecutor  # Changed import

# Paths and constants
results_file = r"C:\Users\USER\Downloads\gen-ai\Forex-Analysis.md"
price_channels_file = r"C:\Users\USER\Downloads\gen-ai\price_channels.md"
output_dir = r"C:\Users\USER\Downloads\gen-ai\output_market_analysis"
recipient = "braimahgifted@gmail.com"
sender = "braimahgifted@gmail.com"
password = "cgjutsrgjrkuxeyq"
subject_line = "Daily Forex Analysis"
attachments = [results_file]

# Lock for thread-safe file access
file_write_lock = Lock()

def sort_files(file_paths):
    """Sorts file paths, placing JSON files before PNG files."""
    def key_function(file_path):
        if isinstance(file_path, str) and file_path.endswith(".json"):
            return 0
        elif isinstance(file_path, str) and file_path.endswith(".png"):
            return 1
        else:
            return 2

    return sorted(file_paths, key=key_function)

def firstStep(sorted_file, mime_types):
    # with file_write_lock:  # Ensure process-safe file access
    #     with open(results_file, "a", encoding="utf-8") as file:
    #         file.write("\n\n" + "-" * 95 + "\n\n")

    try:
        analyzer = GeminiMarketAnalyzer(sorted_file, mime_types)
        analyzer.upload_files()
        analyzer.analyze_market()
    except Exception as e:
        print(f"Error in firstStep: {e}")

def secondStep(sorted_file, mime_types):
    # with file_write_lock:  # Ensure process-safe file access
    #     with open(price_channels_file, "a", encoding="utf-8") as file:
    #         file.write("\n\n" + "-" * 95 + "\n\n")

    try:
        channel = PriceChannelAnalyzer(sorted_file, mime_types)
        channel.upload_files()
        channel.analyze_market()
    except Exception as e:
        print(f"Error in secondStep: {e}")

def analyseFile(args):
    file, mime_types = args
    sorted_file = sort_files(file)
    start_time = time.perf_counter()

    firstStep(sorted_file, mime_types)
    bot1_time = time.perf_counter() - start_time

    secondStep(sorted_file, mime_types)
    bot2_time = time.perf_counter() - start_time

    return {
        "file": sorted_file,
        "bot1_time": bot1_time,
        "bot2_time": bot2_time,
    }

def fx_analyser(pairs):
    pair_group=pairs
    # Initialize results file
    with open(results_file, "w", encoding="utf-8") as file:
        file.write(f"FOREX ANALYSIS FOR {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Retrieve and process files
    files = dataRetriever(pair_group)
    os.makedirs(output_dir, exist_ok=True)  # Create output directory if it doesn't exist
    processed_files = process_files_by_currency(files, output_dir)

    # Flatten processed files
    re_processed_paths = [
        ([item for item in file[0]] + [item for item in file[1]] + [item for item in file[2]])
        for file in processed_files
    ]

    # MIME types used for analysis
    mime_types = [
        "text/plain",
        "text/plain",
        "text/plain",
        "image/png",
        "image/png",
        "image/png",
    ]

    # Parallel processing with ProcessPoolExecutor
    results = []
    worker_count = min(len(re_processed_paths), os.cpu_count())
    start_time = time.perf_counter()

    with ProcessPoolExecutor(max_workers=worker_count) as executor:
        # Pass mime_types to each task
        tasks = [(file, mime_types) for file in re_processed_paths]
        futures = [executor.submit(analyseFile, task) for task in tasks]
        for future in futures:
            try:
                results.append(future.result())
            except Exception as e:
                print(f"Error processing file: {e}")

    # Print results
    for result in results:
        print(f"File: {result['file']}")
        print(f"Bot 1 Time: {result['bot1_time']:.2f} seconds")
        print(f"Bot 2 Time: {result['bot2_time']:.2f} seconds")
        print("---")

    total_time = time.perf_counter() - start_time
    print(f"Total Execution Time: {total_time:.2f} seconds")

    # Send results via email
    # print("Emailing Results")
    # markdown_to_html_email(results_file, recipient, sender, password, subject_line, attachments)

if __name__ == "__main__":
    fx_analyser()
import yfinance as yf
import pandas as pd
import os
import concurrent.futures
import time

class ForexDataProcessor:
    SUPPORTED_PERIODS = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]

    def __init__(self, pairs, output_dir="forex_data"):
        self.forex_pairs = pairs
        # self.forex_pairs = {
        #     "EUR/USD": "EURUSD=X",
        #     "USD/JPY": "JPY=X",
        #     "GBP/USD": "GBPUSD=X",
        #     "USD/CHF": "CHF=X",
        #     "USD/CAD": "CAD=X",
        #     "AUD/USD": "AUDUSD=X",
        #     "NZD/USD": "NZDUSD=X"
        # }
        
        # self.forex_pairs = {
        #     "BTC/USD": "BTC-USD",
        #     "ETH/USD": "ETH-USD",
        #     "XRP/USD": "XRP-USD",
        #     "LTC/USD": "LTC-USD",
        #     "ADA/USD": "ADA-USD",
        #     "DOGE/USD": "DOGE-USD",
        #     "BNB/USD": "BNB-USD",  # Binance Coin
        #     "SOL/USD": "SOL-USD", # Solana
        #     "DOT/USD": "DOT-USD", # Polkadot
        #     "MATIC/USD": "MATIC-USD" # Polygon
        # }
        
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def get_forex_data(self, pair_name, ticker, period, interval):
        try:
            if period not in self.SUPPORTED_PERIODS:
                print(f"Warning: Period '{period}' is not directly supported. Using '3mo' as fallback for {pair_name} ({period}, {interval}).")
                period = '3mo'

            data = yf.download(tickers=ticker, period=period, interval=interval, progress=False)

            if data.empty:
                print(f"Warning: No data found for {pair_name} ({period}, {interval}).")
                return None, pair_name, period, interval

            data_json = data.to_json(date_format="iso", orient="index")
            return data_json, pair_name, period, interval

        except Exception as e:
            print(f"Error fetching data for {pair_name} ({period}, {interval}): {e}")
            return None, pair_name, period, interval

    def process_timeframe(self, timeframe):
        period = timeframe["period"]
        interval = timeframe["interval"]
        file_paths = []

        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = [
                executor.submit(self.get_forex_data, pair, ticker, period, interval)
                for pair, ticker in self.forex_pairs.items()
            ]

            for future in concurrent.futures.as_completed(futures):
                data_json, pair_name, period, interval = future.result()
                if data_json:
                    filename = f"{pair_name.replace('/', '-')}_{period}_{interval}.json"
                    filepath = os.path.join(self.output_dir, filename)
                    try:
                        with open(filepath, 'w') as f:
                            f.write(data_json)
                        print(f"Data for {pair_name} ({period}, {interval}) saved to {filepath}")
                        file_paths.append(filepath)
                    except Exception as e:
                        print(f"Error saving {pair_name} data ({period}, {interval}) to file: {e}")

        return file_paths

    def process_all_timeframes(self, timeframes):
        all_file_paths = []

        with concurrent.futures.ProcessPoolExecutor() as executor:
            timeframe_futures = [
                executor.submit(self.process_timeframe, timeframe) for timeframe in timeframes
            ]
            
            for future in concurrent.futures.as_completed(timeframe_futures):
                all_file_paths.extend(future.result())

        sorted_paths = self.sort_paths_by_currency(all_file_paths)
        return sorted_paths

    def sort_paths_by_currency(self, file_paths):
        sorted_paths = {pair: [] for pair in self.forex_pairs.keys()}

        for path in file_paths:
            for pair in self.forex_pairs.keys():
                if pair.replace('/', '-') in path:
                    sorted_paths[pair].append(path)

        return list(sorted_paths.values())

def dataRetriever(pairs):
    pair_group = pairs
    processor = ForexDataProcessor(pair_group)
    
    timeframes = [
        {"period": "1y", "interval": "1wk"},
        {"period": "3mo", "interval": "1d"},
        {"period": "5d", "interval": "1h"},
    ]

    start_time = time.time()
    sorted_file_paths = processor.process_all_timeframes(timeframes)
    end_time = time.time()

    print("Sorted file paths by currency:")
    for currency_paths in sorted_file_paths:
        print(currency_paths)

    print(f"Finished processing all timeframes in {end_time - start_time:.2f} seconds.")
    return sorted_file_paths

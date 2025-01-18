import pandas as pd
import numpy as np
import mplfinance as mpf
from scipy.signal import argrelextrema
import os


def process_and_plot(file_path, output_dir):
    """Processes a single file, plots the data, and saves the chart."""

    print(f"Processing: {file_path}")
    # Load historical price data with correct format
    try:
        df = pd.read_json(file_path).T  # Transpose to fix structure
        df.index = pd.to_datetime(df.index)  # Convert index to DateTime
        df = df.sort_index()  # Sort by date
        df.reset_index(inplace=True)
        df.rename(columns={"index": "Date"}, inplace=True)  # Rename index to Date
    except Exception as e:
        print(f"Error reading JSON file {file_path}, skipping file with error: {e}")
        return None, None

    # Compute Moving Averages (50 & 200 EMA for trends)
    def ema(series, period):
        return series.ewm(span=period, adjust=False).mean()

    df["EMA_50"] = ema(df["Close"], 50)
    df["EMA_200"] = ema(df["Close"], 200)

    # Detect Trends
    def detect_trend(row):
        if row["EMA_50"] > row["EMA_200"]:
            return "Uptrend"
        elif row["EMA_50"] < row["EMA_200"]:
            return "Downtrend"
        else:
            return "Sideways"

    df["Trend"] = df.apply(detect_trend, axis=1)

    # Detect Support & Resistance (Using Local Extrema)
    def find_support_resistance(df, order=5):
        """Finds local highs and lows for support & resistance detection."""
        df["Support"] = np.nan
        df["Resistance"] = np.nan

        # Local minima (Support)
        local_min = argrelextrema(df["Low"].values, np.less, order=order)[0]
        df.loc[df.index[local_min], "Support"] = df["Low"].iloc[local_min]

        # Local maxima (Resistance)
        local_max = argrelextrema(df["High"].values, np.greater, order=order)[0]
        df.loc[df.index[local_max], "Resistance"] = df["High"].iloc[local_max]

        return df

    df = find_support_resistance(df)

    # Detect Breakouts
    df["Breakout"] = np.where((df["Close"] > df["Resistance"].shift(1)), "Yes", "No")
    df["Breakdown"] = np.where((df["Close"] < df["Support"].shift(1)), "Yes", "No")

    # Detect Consolidation (Using Bollinger Bands & ATR)
    def atr(high, low, close, period=14):
        tr = np.maximum(high - low, np.maximum(abs(high - close.shift()), abs(low - close.shift())))
        return tr.rolling(window=period).mean()

    df["ATR"] = atr(df["High"], df["Low"], df["Close"], period=14)

    def bollinger_bands(series, period=20, std_dev=2):
        sma = series.rolling(window=period).mean()
        std = series.rolling(window=period).std()
        upper_band = sma + (std_dev * std)
        lower_band = sma - (std_dev * std)
        return upper_band, sma, lower_band

    upper_band, middle_band, lower_band = bollinger_bands(df["Close"], period=20, std_dev=2)
    df["Bollinger_Width"] = (upper_band - lower_band) / middle_band  # Normalize width
    df["Consolidation"] = np.where(df["Bollinger_Width"] < 0.05, "Yes", "No")  # Threshold for consolidation

    # Extract currency pair from filename (assuming filename format like "EUR-USD_5d_1h.json")
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    currency_pair = base_name.split('_')[0]

    # Create currency pair specific output directory
    currency_output_dir = os.path.join(output_dir, currency_pair)
    os.makedirs(currency_output_dir, exist_ok=True)

    # Save the processed data
    output_json_path = os.path.join(currency_output_dir, f"{base_name}_processed.json")
    df.to_json(output_json_path, orient="records", date_format="iso")

    # Set 'Date' column as the index for mplfinance plotting
    df.set_index('Date', inplace=True)

    # Check for missing data
    print(f"Missing values before handling for: {file_path}")
    print(df[["Open", "High", "Low", "Close"]].isnull().sum())

    # Remove rows with NaN values
    df = df.dropna(subset=['Open', 'High', 'Low', 'Close'])

    # Check for missing data
    print(f"Missing values after handling for: {file_path}")
    print(df[["Open", "High", "Low", "Close"]].isnull().sum())

    # Ensure correct datetime index
    print(f"DataFrame Index for: {file_path}")
    print(df.index)
    print(f"DataFrame Index dtype: {df.index.dtype}")

    # File path for the saved image
    image_filename = f"{base_name}_chart.png"
    image_path = os.path.join(currency_output_dir, image_filename)

    # Plot Market Structure with Support & Resistance and save as an image
    mpf.plot(
        df,
        type="candle",
        style="charles",
        volume=False,
        title=f"Market Structure Analysis - {base_name}",
        addplot=[
            mpf.make_addplot(df["Support"], scatter=True, marker="v", color="green"),
            mpf.make_addplot(df["Resistance"], scatter=True, marker="^", color="red")
        ],
        savefig=dict(fname=image_path, dpi=300, bbox_inches="tight"),
        warn_too_much_data=False  # Avoid warnings for gaps (e.g., weekends)
    )

    print(f"\u2705 Market structure analysis complete for {file_path}. Processed data saved as '{output_json_path}'.")
    print(f"\u2705 Chart saved as: {image_path}")

    return output_json_path, image_path


def process_files_by_currency(file_lists, output_dir):
    """Processes files grouped by currency pairs."""
    processed_files_by_currency = []

    for currency_files in file_lists:
        processed_files = []
        for file_path in currency_files:
            processed_json, processed_image = process_and_plot(file_path, output_dir)
            if processed_json and processed_image:
                processed_files.append((processed_json, processed_image))
        processed_files_by_currency.append(processed_files)

    return processed_files_by_currency

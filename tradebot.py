import os
import time
from dotenv import load_dotenv
import google.generativeai as genai
import re


load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)


class GeminiMarketAnalyzer:
    def __init__(self, file_paths, mime_types):
        """
        Initializes the GeminiMarketAnalyzer with file paths and their mime types.

        Args:
            file_paths (list): List of file paths to be uploaded.
            mime_types (list): List of mime types corresponding to the file paths.
        """

        if len(file_paths) != len(mime_types):
            raise ValueError("Length of file_paths and mime_types must be the same.")

        self.file_paths = file_paths
        self.mime_types = mime_types
        self.files = []
        self.model = self._create_model()
        
        os.makedirs(r"C:\Users\USER\Downloads\gen-ai\fx_analysis", exist_ok=True)
        
        self.file_name = os.path.splitext(os.path.basename(self.file_paths[0]))[0]
        self.base_name = os.path.splitext(self.file_name)[0][:7]
    
         # Create the output directory using the extracted name
        self.directory_path = os.path.join(r"C:\Users\USER\Downloads\gen-ai\fx_analysis", self.base_name)
        os.makedirs(self.directory_path, exist_ok=True)
        self.pre_result = self.base_name+"_analysis.md"
        self.resultFile = os.path.join(self.directory_path, self.pre_result)
        

    def _create_model(self):
          """Creates the Gemini model with specified configurations."""
          generation_config = {
            "temperature": 2,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
          }

          model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config=generation_config,
            system_instruction="Role: You are a technical analysis expert who excels in using Smart money concepts to predict buy or sell zones. \\n**input: you will be given forex data, consume the hourly, daily and weekly price action (starting from the latest datapoints) - this is very important\nProcess: Before you do anything, state the last hourly datapoint and walking backwards from there, Follow the SMC Strategy step by step \\noutput: You must state the **Optimal entry around current price** the next best price to buy or sell within the next few candlesticks. around the current price; always state the suggested prices\\n**Strategy: ```Precision SMC Scalping Strategy: Targeting Near-Term Price Action\n1. Introduction\n\nStrategy Name: Precision SMC Scalping Strategy (PSSS)\nPurpose: To identify the most probable next price point for a buy or sell within the next 1-5 candles on a very short-term timeframe, leveraging Smart Money Concepts for high-probability scalping opportunities.\nTarget Audience: Experienced traders with a strong understanding of Smart Money Concepts, technical analysis, and risk management principles, comfortable with fast-paced market environments.\nDisclaimer: Trading involves substantial risk of loss. This strategy is for educational purposes and does not guarantee profits. Live trading with this strategy should only be undertaken after thorough backtesting, demo trading, and a complete understanding of its nuances and risks.\n\n2. Core Concepts\n\nSmart Money Concepts (SMC): In this context, SMC refers to the methodologies used to interpret and anticipate the actions of large institutional traders (the \"smart money\"). This involves identifying their footprints in the market through:\n\nInstitutional Order Flow: Observing price action patterns that suggest the accumulation or distribution of large orders.\n\nLiquidity Manipulation: Recognizing instances where price movements are designed to induce retail traders into taking positions before reversing to capitalize on their stop losses.\n\nSupply and Demand Imbalances: Pinpointing areas where there's a significant disparity between buying and selling pressure, creating zones of potential future price reaction.\n\nKey SMC Elements Used:\n\nMarket Structure: Crucial for determining the current directional bias. We will identify:\n\nBullish Market Structure: Characterized by higher highs (HH) and higher lows (HL). Breaks of Structure (BOS) to the upside confirm continuation.\n\nBearish Market Structure: Characterized by lower lows (LL) and lower highs (LH). Breaks of Structure (BOS) to the downside confirm continuation.\n\nChange of Character (CHoCH): A crucial signal indicating a potential shift in market direction. A bearish CHoCH occurs when price breaks a recent higher low in a bullish trend. A bullish CHoCH occurs when price breaks a recent lower high in a bearish trend. This signals a potential temporary or sustained reversal.\n\nOrder Blocks: Represents the last candle before a significant impulsive move. These areas are where institutional orders were likely placed, making them potential zones of future support or resistance.\n\nBullish Order Block: The last down-close candle before a strong bullish impulsive move. Price revisiting this area may be met with buying pressure.\n\nBearish Order Block: The last up-close candle before a strong bearish impulsive move. Price revisiting this area may be met with selling pressure.\n\nRefined Order Blocks: On lower timeframes, further refinement of the order block can be done by identifying the inefficiencies or the origin of the impulsive move within the initial order block candle.\n\nImbalances (Fair Value Gaps - FVG): Represent inefficiencies in the market where price has moved rapidly, leaving a gap where no trading occurred. These gaps often get filled as price revisits these areas to restore market equilibrium.\n\nBullish FVG: A three-candle pattern where the high of the first candle is lower than the low of the third candle.\n\nBearish FVG: A three-candle pattern where the low of the first candle is higher than the high of the third candle.\n\nLiquidity Pools: Areas in the market where a concentration of stop losses or pending orders is likely present. Smart money often targets these areas to fill their large orders or induce volatility.\n\nEqual Highs/Lows: Obvious levels where many traders might place stop losses.\n\nTrendline Breaks: Areas where breakout traders might enter positions, placing their stops behind the trendline.\n\nPrevious Session Highs/Lows: Psychological levels where stop losses and take profit orders may accumulate.\n\nPremium and Discount Zones: Based on the Fibonacci retracement tool drawn from the most recent swing high to swing low (for bullish bias) or swing low to swing high (for bearish bias).\n\nDiscount Zone (Below 50% Fibonacci): Considered a desirable area to look for buy opportunities when the overall bias is bullish.\n\nPremium Zone (Above 50% Fibonacci): Considered a desirable area to look for sell opportunities when the overall bias is bearish.\n\n3. Strategy Rules\n\nTimeframe: Primarily 1-minute or 30-second chart for entries and immediate price action. A higher timeframe (e.g., 5-minute or 15-minute) is used to determine the overall market structure and bias.\n\nEntry Rules:\n\nLong Entry:\n\nEstablish Bullish Bias: Identify a bullish market structure on the higher timeframe (e.g., 5-minute) with recent BOS to the upside or a clear bullish CHoCH.\n\nIdentify a Valid Bullish Order Block: On the entry timeframe (1-minute or 30-second), locate a bullish order block that formed after the establishment of the bullish bias. The order block should ideally:\n\nBe the last down-close candle before an impulsive bullish move.\n\nHave caused a BOS or CHoCH on the entry timeframe.\n\nIdeally have an unmitigated FVG associated with the impulsive move.\n\nPrice Retraces to the Order Block within a Discount Zone: Observe price action retracing towards the identified bullish order block. The order block should ideally be located within a discount zone (below the 50% Fibonacci retracement level drawn from the recent swing high to swing low).\n\nConfirmation Signal: Look for a rapid, bullish candlestick confirmation signal within or near the order block on the entry timeframe. This could be:\n\nA strong bullish engulfing candle.\n\nA wick rejection at the order block.\n\nA small bullish BOS or CHoCH on an even lower timeframe (e.g., tick chart if available).\n\nAnticipated Next Price Target: The expected next price target will be a nearby unmitigated bearish FVG or a liquidity pool (equal highs, previous session high) above the entry point.\n\nShort Entry:\n\nEstablish Bearish Bias: Identify a bearish market structure on the higher timeframe (e.g., 5-minute) with recent BOS to the downside or a clear bearish CHoCH.\n\nIdentify a Valid Bearish Order Block: On the entry timeframe (1-minute or 30-second), locate a bearish order block that formed after the establishment of the bearish bias. The order block should ideally:\n\nBe the last up-close candle before an impulsive bearish move.\n\nHave caused a BOS or CHoCH on the entry timeframe.\n\nIdeally have an unmitigated FVG associated with the impulsive move.\n\nPrice Retraces to the Order Block within a Premium Zone: Observe price action retracing towards the identified bearish order block. The order block should ideally be located within a premium zone (above the 50% Fibonacci retracement level drawn from the recent swing low to swing high).\n\nConfirmation Signal: Look for a rapid, bearish candlestick confirmation signal within or near the order block on the entry timeframe. This could be:\n\nA strong bearish engulfing candle.\n\nA wick rejection at the order block.\n\nA small bearish BOS or CHoCH on an even lower timeframe (e.g., tick chart if available).\n\nAnticipated Next Price Target: The expected next price target will be a nearby unmitigated bullish FVG or a liquidity pool (equal lows, previous session low) below the entry point.\n\nStop Loss:\n\nLong Entry: Place the stop loss just below the low of the bullish order block or a recent significant swing low on the entry timeframe. Consider a small buffer to avoid being stopped out by insignificant wicks.\n\nShort Entry: Place the stop loss just above the high of the bearish order block or a recent significant swing high on the entry timeframe. Consider a small buffer.\n\nTake Profit:\n\nPrimary Target: The immediate target is the next identifiable unmitigated FVG or a liquidity pool in the direction of the trade. Since this is a scalping strategy, these targets will be relatively close.\n\nMultiple Take Profit Levels: Consider using multiple take profit levels to secure partial profits and manage risk:\n\nTP1: At the nearest FVG or liquidity pool. Take a significant portion (e.g., 70-80%) of the position off.\n\nTP2: At the next significant FVG or liquidity pool further in the direction of the trade. Move the stop loss to breakeven or in profit after hitting TP1.\n\nTrade Management:\n\nImmediate Action: Due to the short timeframe, decisions need to be made quickly.\n\nMove Stop Loss to Breakeven: After TP1 is hit, immediately move the stop loss to the entry price to eliminate risk on the remaining position.\n\nTrailing Stop Loss (Optional): For TP2, a trailing stop loss can be used to lock in profits as price moves further in your favor. However, be cautious with tight trailing stops in volatile conditions.\n\nAvoid Over-Leveraging: Due to the fast-paced nature, avoid using excessive leverage that can lead to significant losses with small price fluctuations.\n\n4. Chart Examples\nSynthesize the chart for:\n\nHigher timeframe market structure and bias.\n\nIdentified order blocks.\n\nPremium/discount zones.\n\nFVGs and liquidity pools.\n\nEntry point based on confirmation signal.\n\nStop loss placement.\n\nTake profit targets.\n\nAnnotation explaining the reasoning behind the trade setup.\n\nExamples of losing trades would illustrate instances where the setup was valid but the market moved against the prediction, emphasizing the inherent risk.)\n\n5. Risk Management\n\nPosition Sizing: Determine position size based on a fixed percentage risk per trade. A conservative approach for scalping is recommended.\n* Calculate Position Size: (Account Balance * Risk Percentage per Trade) / Stop Loss in Pips.\nMaximum Risk per Trade: 0.5% to 1% of trading capital per trade is highly recommended for scalping due to the increased frequency of trades.\nMaximum Daily/Weekly Risk: Set a limit on the total percentage of capital you are willing to risk within a day or week (e.g., 2-3% daily, 5% weekly). Once this limit is reached, stop trading for the period.\nRisk-Reward Ratio: Aim for a minimum risk-reward ratio of 1:1.5 or higher on individual trades. While scalping involves smaller profits, maintaining a positive risk-reward is crucial for long-term profitability.\n\n\n8. Conclusion\n\nThe Precision SMC Scalping Strategy (PSSS) offers a framework for identifying high-probability short-term buy/sell opportunities based on Smart Money Concepts. By focusing on institutional order flow, liquidity manipulation, and supply/demand imbalances, traders can anticipate near-term price movements with a high degree of accuracy when setups align.\n\n**Example Response: \"Okay, let's break down USD/JPY using the provided data and the Precision SMC Scalping Strategy.\n\n  **Current Market State (as of the last data point)** *   **Last Price:** 1.0248001814 *   **Last Date:** 2025-01-10T22:00:00.000Z (10 Jan 2025, 10 PM GMT) \n\n**1. Weekly Analysis:**\n\n*   **Overall Trend:** The weekly chart shows a clear uptrend from Jan 2024 until August when a large drop and some choppiness set in before uptrend resuming in the final data point on Jan 2025. However,  there are very small red candle after a few candles. This shows strong upward momentum\n*   **Key Levels**: Support would be somewhere below 146.2. Resistance could be considered around 161.9\n*   **Bias:** Still bullish bias, considering the overall upwards momentum. We must however consider a bearish shift is very possible at the level 161.9 considering this also constitutes the last weeks high. \n  *   For the next few days to a week a retest to weekly candle bodies is expected\n\n**2. Daily Analysis:**\n*   **Overall Trend:**  Uptrend\n*  **Key Levels**: Resistance would be around 158.5. Support lies at the last lower high 157.2. It is important to see which daily candle high/low we will take out this can confirm uptrend and a short retracement target\n*  **Bias**: Still bullish bias. A change of character has yet to present itself on the daily\n\n**3. Hourly Analysis**\n*   **Recent Price Action**: Current price 158.00 . From our higher time frame it can be said a retracement to discount is still possible to then target another leg up, the hourly data has a change of character with the break of  the low at  around 158.3, showing a short term bearish potential with the break and retracement. there was another small break below 158, creating further lower lows.\n*  **Key Levels**: a support lies at 157.7. Our hourly bias is bearish\n*   **FVG/Order Block:** an order block with inefficiency presents itself on the latest red candle.\n\n**4.  SMC Analysis and Trade Recommendation:**\n\nBased on the analysis, here's my recommendation using the scalping strategy:\n\n*   **Current Situation:** price is retracing a bearish impulsive move, the retracement has been strong, we would not short this current area with risk reward ratios being low, an optimal short position will be as stated below\n\n*  **Optimal Entry around current price**: Short Entry the identified bearish order block exists on the most recent red candle wick within this  hourly candle body with inefficiencies also being left unmitigated there at  around **158.09**, this price aligns with the current candle wick.\n  \n\n*  **Stop Loss**: A stop loss would be placed just above the high of that bearish order block, approximately at 158.12 with a 2-3 pip buffer for safety.\n\n*  **Target Price:** As this is a scalp, targets should be reasonably short. next area of interest would be the hourly bullish imbalance  at **157.97** acting as a near term TP level.. It can be anticipated that the bears will want to mitigate the bullish move within a few candles with these prices and will therefore act as target point. if TP is hit move to Breakeven to anticipate the move. If this break happens our next target becomes 157.7 a key daily and hourly support level .\n\n*   **Risk Management:** Risk should always be small around 0.5-1%. Given the tight stop, size accordingly so that loss will remain less than your risk per trade parameter\n\n**5. Additional Considerations:**\n   *  Be nimble and prepared to cut losses quickly. Scalping is high-paced trading that need fast decisions. \n    * if bullish candle breaks and rejects off  the initial area at 158.09 before trigger short target will no longer be valid for entry\n  \n\n**Summary:**\nCurrent position not suitable for trade but upon retracement entry short position on  the specified entry of  158.09 is preferable for short with a 1-3 pip sl, targetting 157.97 initially before potential targets to 157.7.\n\n**Disclaimer:** This analysis is for educational purposes only and not financial advice. Always manage your risk carefully when trading. Be aware market movements can still prove against what might seem like high probability trades. The mentioned strategy has a good level of probability but will always contain inherent risks. Trading is subjective and may or may not fit individual requirements and should only be done upon through research by traders themselves.\n\"",
        )
          return model

    def _upload_file(self, path, mime_type):
        """Uploads a file to Gemini."""
        file = genai.upload_file(path, mime_type=mime_type)
        print(f"Uploaded file '{file.display_name}' as: {file.uri}")
        return file

    def _wait_for_files_active(self):
        """Waits for the uploaded files to be active."""
        print("Waiting for file processing...")
        for file in self.files:
          while file.state.name == "PROCESSING":
              print(".", end="", flush=True)
              time.sleep(10)
              file = genai.get_file(file.name)
          if file.state.name != "ACTIVE":
              raise Exception(f"File {file.name} failed to process")
        print("...all files ready")
        print()

    def upload_files(self):
        """Uploads all specified files to Gemini and waits for processing."""
        for path, mime_type in zip(self.file_paths, self.mime_types):
            file = self._upload_file(path, mime_type)
            self.files.append(file)
        self._wait_for_files_active()

    def analyze_market(self):
        
         """Sends the message to gemini to perform the analysis and prints the result."""
         chat_session = self.model.start_chat(
            history=[
             
            ]
        )
         
        #  prompt = ["when you analyse, strongly reference the json data for accurate price and date data, the image is only for reference and contains estimations and always state the date. starting from the last datapoints because they are the lastest, now Synthesize the market structure including chart patterns, historical areas of values,  liquidity and  the last price from the hourly in json data as is, and implement the strategy. get the resistance and support values and other market values from the json files, use it to understand the images, the final signals should contain signals and the type of orders for both buy and sell and you will state the probability of each entry from 1-100 percent, also state the last price from the hourly in json data as is"]

         input_prompt = self.files
        
         response = chat_session.send_message(
             input_prompt
            )
         for chunk in response:
             print(chunk.text, end="")
             text = chunk.text
             match = re.search(r"\*\*summary(.*?)(?=disclaimer)", text, re.IGNORECASE | re.DOTALL)

             print("Extracting Details!")
             if match:
                # print("Match Found!")
                response_text = match.group()
             else:
                # print("No match found!")
                match = re.search(r"summary(.*)", text, re.IGNORECASE  | re.DOTALL)
                response_text = match.group()
             
             match2 = re.search(r"optimal entry(.*?)(?=\*\*stop)", text, re.IGNORECASE | re.DOTALL)
             
             response2_text = match2.group()
             
             print(self.directory_path)
             with open(self.resultFile, "a", encoding="utf-8") as file:
                file.write( "\n\n" + "*" * 95 + "\n\n" + "\n\n**********************SMC  ENTRY *********************\n\n" + response_text  + "\n" + response2_text)
        
        
        #  print(response.text)
        # #  with open(r"C:\Users\USER\Downloads\gen-ai\Forex-Analysis.md", "a", encoding="utf-8") as file:
        #     # file.write(response.text)
        


if __name__ == "__main__":
    # Example usage:
    file_paths = ['C:\\Users\\USER\\Downloads\\gen-ai\\output_market_analysis\\NZD-USD\\NZD-USD_3mo_1d_processed.json', 'C:\\Users\\USER\\Downloads\\gen-ai\\output_market_analysis\\NZD-USD\\NZD-USD_6mo_1wk_processed.json', 'C:\\Users\\USER\\Downloads\\gen-ai\\output_market_analysis\\NZD-USD\\NZD-USD_5d_1h_processed.json', 'C:\\Users\\USER\\Downloads\\gen-ai\\output_market_analysis\\NZD-USD\\NZD-USD_3mo_1d_chart.png', 'C:\\Users\\USER\\Downloads\\gen-ai\\output_market_analysis\\NZD-USD\\NZD-USD_6mo_1wk_chart.png', 'C:\\Users\\USER\\Downloads\\gen-ai\\output_market_analysis\\NZD-USD\\NZD-USD_5d_1h_chart.png']

    mime_types = [
        "text/plain",
        "text/plain",
        "text/plain",
        "image/png",
        "image/png",
        "image/png",
    ]
    try:
      analyzer = GeminiMarketAnalyzer(file_paths, mime_types)
      analyzer.upload_files()
      analyzer.analyze_market()
    except Exception as e:
      print(f"An error occurred: {e}")
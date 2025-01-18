
# Forex and Crypto Market Analyzer

This project provides a comprehensive market analysis tool for both Forex and Cryptocurrency pairs, leveraging the power of AI (specifically Google's Gemini) for technical analysis and generating trading signals. It retrieves historical data, performs technical analysis using Smart Money Concepts (SMC) and Wyckoff methodology, and delivers the results via email.

## Table of Contents

* [Project Overview](#project-overview)
* [Features](#features)
* [Getting Started](#getting-started)
    * [Prerequisites](#prerequisites)
    * [Installation](#installation)
    * [Configuration](#configuration)
    * [Usage](#usage)
    * [Arguments](#arguments)
* [Project Structure](#project-structure)
* [Modules and Functionality](#modules-and-functionality)
    * [`forex_mailer.py`](#forex_mailerpy)
    * [`forexApp.py`](#forexapppy)
    * [`fx.py`](#fxpy)
    * [`price_channels.py`](#price_channelspy)
    * [`tradebot.py`](#tradebotpy)
    * [`trade.py`](#tradepypy)
    * [`tradde.py`](#traddepypy)
* [Technical Analysis Strategies](#technical-analysis-strategies)
    * [Smart Money Concepts (SMC)](#smart-money-concepts-smc)
    * [Wyckoff Method](#wyckoff-method)
* [Parallel Processing](#parallel-processing)
* [Email Integration](#email-integration)
* [Error Handling](#error-handling)
* [Contributing](#contributing)
* [License](#license)
* [Disclaimer](#disclaimer)
* [Contact](#contact)
* [Acknowledgements](#acknowledgements)



## Project Overview

This project aims to automate the process of technical analysis for Forex and Crypto markets using AI-powered insights. It combines data retrieval, technical analysis using SMC and Wyckoff strategies, signal generation, and email delivery into a single, streamlined workflow. The analysis results are presented in an easy-to-understand format, enabling traders to make more informed decisions.

## Features

* **Automated Data Retrieval:** Retrieves historical market data for specified Forex and Crypto pairs using `yfinance`.
* **AI-Powered Technical Analysis:** Employs Google's Gemini AI model to perform technical analysis based on SMC and Wyckoff principles.
* **Smart Money Concepts (SMC) Analysis:** Identifies potential buy/sell zones by analyzing order flow, liquidity manipulation, and supply/demand imbalances.
* **Wyckoff Method Analysis:** Predicts short-term market direction based on price and volume patterns, identifying accumulation and distribution phases.
* **Signal Generation:** Generates trading signals with entry points, stop-loss levels, and target prices.
* **Email Notifications:** Sends analysis results and charts as HTML emails with attachments.
* **Parallel Processing:** Utilizes multiprocessing to speed up the analysis process.
* **Customizable Parameters:** Allows for customization of analysis parameters, such as timeframes and trading pairs.
* **Error Handling and Logging:** Includes error handling mechanisms to ensure robustness and provides logging for debugging.

## Getting Started


### Prerequisites

* **Python 3.7 or higher:** Ensure you have a compatible Python version installed.
* **Required Libraries:** Install the necessary Python packages using:
```bash
pip install -r requirements.txt
```
The `requirements.txt` file should contain the following:

```
mistune
yfinance
pandas
mplfinance
scipy
google-generativeai
python-dotenv
```

* **Google Cloud Project and API Key:** Create a Google Cloud project, enable the Gemini API, and obtain an API key. Store the API key in an environment variable named `GOOGLE_API_KEY`.  See the [Gemini documentation](https://developers.generativeai.google/) for details.
* **(Optional) Gmail Account for Email:** If you want to use the email notification feature, you'll need a Gmail account and an app-specific password.


### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/forex-crypto-analyzer.git  # Replace with your repository URL
```

2. Navigate to the project directory:
```bash
cd forex-crypto-analyzer
```


### Configuration

1. **API Key:** Set the `GOOGLE_API_KEY` environment variable with your Gemini API key. You can do this in your shell startup file (e.g., `.bashrc`, `.zshrc`) or by setting it directly in the terminal:

   ```bash
   export GOOGLE_API_KEY="YOUR_API_KEY"  # Replace with your actual API key
   ```

2. **Email Credentials (Optional):** If using the email feature, update the `sender`, `password`, and `recipient` variables in `forexApp.py` and `fx.py` with your Gmail credentials.  It is **strongly recommended** to use an app-specific password for security.

3. **File Paths:** Adjust the file paths in the scripts (`forexApp.py`, `fx.py`, `price_channels.py`, `tradebot.py`, `trade.py`, `tradde.py`) if you want to store data and results in different locations.


### Usage

To run the analysis, execute the `fx.py` script with a command-line argument:

* For Forex analysis:
```bash
python fx.py forex
```

* For Crypto analysis:
```bash
python fx.py btc
```


### Arguments

The `fx.py` script accepts one argument:

* `forex` (or any other string except "btc"): Runs the analysis for Forex pairs.
* `btc`: Runs the analysis for Cryptocurrency pairs.


## Project Structure

```
forex-crypto-analyzer/
├── forex_mailer.py       # Module for sending email notifications
├── forexApp.py          # Main application script for Forex/Crypto analysis
├── fx.py                 # Entry point script with argument handling
├── price_channels.py     # Module for Wyckoff analysis
├── tradebot.py          # Module for SMC analysis
├── trade.py             # Module for data retrieval and processing
├── tradde.py            # Module for chart generation and support/resistance detection
└── requirements.txt       # List of project dependencies
```




## Modules and Functionality



### `forex_mailer.py`

This module handles sending email notifications with HTML content and attachments.

* **`markdown_to_html_email()`:** Converts a Markdown file to HTML and sends it as an email with optional attachments.



### `forexApp.py`

This script orchestrates the market analysis process.

* **`sort_files()`:** Sorts file paths, prioritizing JSON files.
* **`firstStep()`:** Executes the SMC analysis using `tradebot.py`.
* **`secondStep()`:** Executes the Wyckoff analysis using `price_channels.py`.
* **`analyseFile()`:** Processes a single set of files (JSON and PNG).
* **`fx_analyser()`:** Main function that retrieves data, processes it, performs analysis, and (optionally) sends emails.



### `fx.py`

This script is the main entry point for the project.

* **`forex_signals()`:** Uses Gemini to generate trading signals from the analysis results.
* **`main()`:** Handles command-line arguments, runs the analysis, and sends email notifications.




### `price_channels.py`

This module performs technical analysis based on the Wyckoff method using Gemini.

* **`PriceChannelAnalyzer` class:**
    * **`__init__()`:** Initializes the analyzer, creates the Gemini model, and sets up file paths.
    * **`_create_model()`:** Creates the Gemini model with specified configurations.
    * **`_upload_file()`:** Uploads a file to Gemini.
    * **`_wait_for_files_active()`:** Waits for uploaded files to become active.
    * **`upload_files()`:** Uploads all specified files.
    * **`analyze_market()`:** Performs the Wyckoff analysis using Gemini and saves the results.




### `tradebot.py`

This module performs technical analysis based on Smart Money Concepts using Gemini.

* **`GeminiMarketAnalyzer` class:**  (Similar structure and methods as `PriceChannelAnalyzer` in `price_channels.py`)



### `trade.py`

This module handles data retrieval and processing using `yfinance`.

* **`ForexDataProcessor` class:**
    * **`__init__()`:** Initializes the data processor.
    * **`get_forex_data()`:** Downloads data for a specific pair, period, and interval.
    * **`process_timeframe()`:** Processes data for a given timeframe (period and interval).
    * **`process_all_timeframes()`:** Processes data for all specified timeframes.
    * **`sort_paths_by_currency()`:** Sorts file paths by currency pair.
* **`dataRetriever()`:** Retrieves data for specified pairs and timeframes.





### `tradde.py`

This module handles plotting, support/resistance detection, and saving charts as images.

* **`process_and_plot()`:** Processes a single data file, generates a chart, and saves it as a PNG image.
* **`process_files_by_currency()`:** Processes a list of files grouped by currency pair.




## Technical Analysis Strategies

### Smart Money Concepts (SMC)

This strategy focuses on identifying the actions of institutional traders ("smart money") by analyzing order flow, liquidity, and supply/demand imbalances. It uses concepts like market structure, order blocks, imbalances, and liquidity pools to predict near-term price movements.

### Wyckoff Method

This method predicts market direction by analyzing price and volume patterns, identifying accumulation and distribution phases. It looks for specific events like Preliminary Support (PS), Selling Climax (SC), Automatic Rally (AR), Secondary Test (ST), and Spring (in accumulation) or their distribution phase equivalents to predict price movements.

## Parallel Processing

The project utilizes the `concurrent.futures` module to perform data retrieval and analysis in parallel, significantly reducing processing time. The `ProcessPoolExecutor` is used for process-based parallelism, taking advantage of multiple CPU cores.

## Email Integration

The `forex_mailer.py` module provides functionality to send email notifications with HTML content and attachments. This allows users to receive the analysis results and charts directly in their inbox.  Uses `smtplib` and the `email` modules.  Requires a Gmail account (or other SMTP server configuration).


## Error Handling

The code includes error handling mechanisms (`try...except` blocks) to gracefully handle potential errors during data retrieval, processing, and analysis. Error messages are printed to the console to assist with debugging.

## Contributing

Contributions to this project are welcome. Please follow these guidelines:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with clear commit messages.
4. Push your branch to your forked repository.
5. Create a pull request to the main repository.


## License

This project is licensed under the [MIT License](LICENSE).


## Disclaimer

This project is for educational and informational purposes only. It should not be considered financial advice. Trading in financial markets involves substantial risk, and you should consult with a qualified financial advisor before making any investment decisions.  The AI-generated analysis and trading signals are not guaranteed to be accurate and should not be solely relied upon for making trading decisions.


## Contact

For any inquiries or feedback, please contact braimahgifted@gmail.com.


## Acknowledgements

* **yfinance:** For providing a convenient way to retrieve financial data.
* **mplfinance:** For creating financial charts.
* **scipy:** For scientific computing functions used in analysis.
* **Google Gemini:** For powering the AI-driven technical analysis.


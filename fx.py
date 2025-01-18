from datetime import datetime
from forexApp import fx_analyser
import os
import google.generativeai as genai
from forex_mailer import markdown_to_html_email
import sys  # Import the sys module

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

def forex_signals(file, name):
    result_file = file
    file_name = name
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config=generation_config,
        system_instruction="you will be given a text containing the results of a trading analysis. there are three \"SMC Entries\" containing \"optimal entry price\" and three \"Wyckoff analysis\" containg the \"short term prediction\". you are to extract and summarize each \"SMC Entry\" and \"Wyckoff analysis\" in no more than 1 sentence, make sure to include the summary. \n\nexample reponse: \"Here are the Results of the Analysis:\n\n**Wyckoff Analysis:**\n\n*   **Wyckoff Analysis 1:** The analysis predicts continued downward movement with a small bounce near 0.6218 before a further decline towards 0.62.\n*   **Wyckoff Analysis 2:** Expect sideways consolidation before a likely downward move towards 0.613, with short entries on rejections of a validated hourly distribution pattern.\n*   **Wyckoff Analysis 3:** The market may move sideways with potential for a downside move, with a bearish bias unless a strong bullish breakout confirms otherwise.\n\"\n\n**SMC Entries:**\n\n*   **SMC Entry 1:** A short entry is suggested around 0.6215 upon rejection with a target of 0.619, while a long entry is possible at 0.618 with a quick stop loss.\n*   **SMC Entry 2:** A short entry is recommended at 0.6212 targeting 0.6206-0.6207 initially, potentially extending to 0.6199.\n*   **SMC Entry 3:** A short entry is preferred at a specified zone, while a long position is only considered at 0.6197, both with tight stop losses and targets.\n\n**Summary:**\n*   **Wyckoff: The first analysis predicts a continued downward movement immediately while the second and third analysis predicts a sideways movement first then downtrend\n*   **SMC:  Preferred entries 1. Short - 0.6215     2. short - 0.6212    3. short - at specified zone\n",
    )

    chat_session = model.start_chat(
        history=[
        ]
    )

    print("Analysing " + file_name)
    md_content = ""
    with open(result_file, "r", encoding="utf-8") as file:
        md_content = file.read()

    response = chat_session.send_message(md_content)

    with open(result_file, "w", encoding="utf-8") as file:
        file.write(response.text)

    print("Finished Analysis for: " + file_name)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide an argument ('btc' for crypto, anything else for forex).")
        sys.exit(1)

    argument = sys.argv[1].lower()

    forex_pairs_list = [
        {
            "EUR/USD": "EURUSD=X",
            "USD/JPY": "JPY=X",
            "GBP/USD": "GBPUSD=X",
            "USD/CHF": "CHF=X",
            "USD/CAD": "CAD=X"
        },
        {
            "AUD/USD": "AUDUSD=X",
            "NZD/USD": "NZDUSD=X",
            "GBP/JPY": "GBPJPY=X",
            "EUR/JPY": "EURJPY=X",
            "EUR/GBP": "EURGBP=X"
        }
    ]

    crypto_pairs_list = [
        {
            "BTC/USD": "BTC-USD",
            "BNB/USD": "BNB-USD",
            "SOL/USD": "SOL-USD",
            "AVAX/USD": "AVAX-USD",
            "LINK/USD": "LINK-USD"
        },
        {
            "UNI/USD": "UNI-USD",
            "LTC/USD": "LTC-USD",
            "DOGE/USD": "DOGE-USD",
            "XRP/USD": "XRP-USD",
            "ADA/USD": "ADA-USD"
        }
    ]

    if argument == "btc":
        pairs = crypto_pairs_list
    else:
        pairs = forex_pairs_list

    for pair_group in pairs:
        for _ in range(3):  # Run fx_analyser 3 times for each pair
            fx_analyser(pair_group)

        print("Emailing Results")

        file_list = []
        for root, _, files in os.walk(r"C:\Users\USER\Downloads\gen-ai\fx_analysis"):
            for file in files:
                file_list.append(os.path.abspath(os.path.join(root, file)))
        print(file_list)

        for file in file_list:
            file_name = os.path.splitext(os.path.basename(file))[0]

            forex_signals(file, file_name)

            markdown_file = file
            recipient = "braimahgifted@gmail.com"
            sender = "braimahgifted@gmail.com"
            password = "cgjutsrgjrkuxeyq"
            subject_line = file_name
            attachments = [
                file,
            ]

            markdown_to_html_email(markdown_file, recipient, sender, password, subject_line, attachments)
            os.remove(markdown_file)

        print("All tasks have been completed and email sent")
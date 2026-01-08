import os
import yfinance as yf
import telegram
import google.generativeai as genai
from portfolio import Portfolio
import time
from options import find_bullish_opportunities

# --- Configuration ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
STOCKS_TO_MONITOR = ["GOOGL", "MSFT", "AAPL", "AMZN"]

# --- Main Application ---

def get_stock_data(ticker):
    """Fetches stock data for a given ticker, including the 50-day moving average."""
    stock = yf.Ticker(ticker)
    hist = stock.history(period="3mo") # Get 3 months of data for moving average
    data = stock.info
    data['fiftyDayAverage'] = hist['Close'].rolling(window=50).mean().iloc[-1]
    return data

def send_telegram_alert(message):
    """Sends a message to your Telegram bot."""
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

def get_gemini_analysis(prompt):
    """Gets financial analysis from Gemini."""
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text

def main():
    """Main function to run the autonomous monitoring bot."""
    portfolio = Portfolio(starting_cash=100000.0)

    while True:
        print("--- Checking Stocks ---")
        for ticker in STOCKS_TO_MONITOR:
            try:
                stock_data = get_stock_data(ticker)
                current_price = stock_data['regularMarketPrice']
                fifty_day_average = stock_data['fiftyDayAverage']
                
                print(f"{ticker}: Price ${current_price:.2f}, 50-Day Avg: ${fifty_day_average:.2f}")

                # --- Trading Logic ---
                # Buy if price is 5% below 50-day average
                if current_price < fifty_day_average * 0.95:
                    if portfolio.buy(ticker, 10): # Buy 10 shares
                        prompt = f"I just bought 10 shares of {ticker} at ${current_price:.2f} because it was 5% below its 50-day moving average. What is the outlook for this stock?"
                        analysis = get_gemini_analysis(prompt)
                        message = f"PAPER TRADE: Bought 10 {ticker} @ ${current_price:.2f}\n\n{analysis}"
                        send_telegram_alert(message)

                # Sell if price is 5% above 50-day average
                elif current_price > fifty_day_average * 1.05:
                    if portfolio.holdings.get(ticker) and portfolio.holdings[ticker].get('shares', 0) > 0:
                        if portfolio.sell(ticker, 10): # Sell 10 shares
                            prompt = f"I just sold 10 shares of {ticker} at ${current_price:.2f} because it was 5% above its 50-day moving average. Was this a good move?"
                            analysis = get_gemini_analysis(prompt)
                            message = f"PAPER TRADE: Sold 10 {ticker} @ ${current_price:.2f}\n\n{analysis}"
                            send_telegram_alert(message)

                # --- Options Logic ---
                options_opportunities = find_bullish_opportunities(ticker)
                if options_opportunities:
                    for opp in options_opportunities:
                        # Only alert for options with some volume
                        if opp['volume'] > 10 and opp['open_interest'] > 20:
                             prompt = f"I've identified a potential bullish call option for {ticker}. The strike price is ${opp['strike']} with an expiration of {opp['expiration']}. The current volume is {opp['volume']} and open interest is {opp['open_interest']}. Should I consider this trade?"
                             analysis = get_gemini_analysis(prompt)
                             message = (f"OPTIONS ALERT: Bullish opportunity for {ticker}!\n"
                                       f"Type: {opp['type']}, Strike: ${opp['strike']:.2f}, Exp: {opp['expiration']}\n"
                                       f"Last Price: ${opp['last_price']:.2f}, Vol: {opp['volume']}, OI: {opp['open_interest']}\n\n"
                                       f"Gemini Analysis:\n{analysis}")
                             send_telegram_alert(message)


            except Exception as e:
                print(f"Error processing {ticker}: {e}")

        print(portfolio)
        print("--- Waiting for next check... ---")
        time.sleep(300) # Wait for 5 minutes (300 seconds)

if __name__ == "__main__":
    main()

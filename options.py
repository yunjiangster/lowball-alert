import yfinance as yf

def find_bullish_opportunities(ticker):
    """Finds potentially bullish call option opportunities."""
    opportunities = []
    try:
        stock = yf.Ticker(ticker)
        
        # Get current stock price
        current_price = stock.history(period="1d")['Close'].iloc[-1]

        # Get the next expiration date
        expirations = stock.options
        if not expirations:
            return opportunities
        next_expiration = expirations[0]

        # Get the option chain for the next expiration date
        opt = stock.option_chain(next_expiration)
        calls = opt.calls

        # Find calls that are slightly out-of-the-money (e.g., strike price is 0-5% above current price)
        for index, row in calls.iterrows():
            strike = row['strike']
            if current_price < strike < current_price * 1.05:
                opportunity = {
                    'ticker': ticker,
                    'type': 'Call',
                    'strike': strike,
                    'expiration': next_expiration,
                    'last_price': row['lastPrice'],
                    'volume': row['volume'],
                    'open_interest': row['openInterest']
                }
                opportunities.append(opportunity)
                
    except Exception as e:
        print(f"Error finding options for {ticker}: {e}")

    return opportunities

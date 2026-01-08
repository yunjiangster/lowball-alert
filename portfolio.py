import yfinance as yf

class Portfolio:
    """Manages a paper trading portfolio."""

    def __init__(self, starting_cash=100000.0):
        """Initializes the portfolio."""
        self.cash = starting_cash
        self.holdings = {}  # {ticker: {"shares": float, "avg_price": float}}
        self.transaction_fee = 7.95  # Example transaction fee

    def buy(self, ticker, shares):
        """Buys a specified number of shares of a stock."""
        try:
            stock = yf.Ticker(ticker)
            price = stock.history(period="1d")['Close'].iloc[-1]
            cost = (shares * price) + self.transaction_fee

            if self.cash < cost:
                print(f"Error: Not enough cash to buy {shares} shares of {ticker}.")
                return False

            self.cash -= cost

            if ticker in self.holdings:
                # Update existing holding
                current_shares = self.holdings[ticker]['shares']
                current_avg_price = self.holdings[ticker]['avg_price']
                new_total_shares = current_shares + shares
                new_total_cost = (current_shares * current_avg_price) + (shares * price)
                self.holdings[ticker]['shares'] = new_total_shares
                self.holdings[ticker]['avg_price'] = new_total_cost / new_total_shares
            else:
                # Add new holding
                self.holdings[ticker] = {'shares': shares, 'avg_price': price}
            
            print(f"Bought {shares} shares of {ticker} at ${price:.2f} each.")
            return True
        except Exception as e:
            print(f"Error buying {ticker}: {e}")
            return False

    def sell(self, ticker, shares):
        """Sells a specified number of shares of a stock."""
        if ticker not in self.holdings or self.holdings[ticker]['shares'] < shares:
            print(f"Error: You don't own enough shares of {ticker} to sell.")
            return False
        
        try:
            stock = yf.Ticker(ticker)
            price = stock.history(period="1d")['Close'].iloc[-1]
            proceeds = (shares * price) - self.transaction_fee

            self.cash += proceeds
            self.holdings[ticker]['shares'] -= shares

            if self.holdings[ticker]['shares'] == 0:
                del self.holdings[ticker]

            print(f"Sold {shares} shares of {ticker} at ${price:.2f} each.")
            return True
        except Exception as e:
            print(f"Error selling {ticker}: {e}")
            return False

    def get_holdings_value(self):
        """Calculates the total value of all holdings."""
        holdings_value = 0.0
        for ticker, data in self.holdings.items():
            try:
                stock = yf.Ticker(ticker)
                price = stock.history(period="1d")['Close'].iloc[-1]
                holdings_value += data['shares'] * price
            except Exception as e:
                print(f"Could not retrieve current price for {ticker}: {e}")
        return holdings_value

    def get_total_value(self):
        """Calculates the total value of the portfolio (cash + holdings)."""
        return self.cash + self.get_holdings_value()

    def __str__(self):
        """String representation of the portfolio."""
        holdings_list = []
        for ticker, data in self.holdings.items():
            holdings_list.append(f"  - {ticker}: {data['shares']} shares @ avg ${data['avg_price']:.2f}")
        holdings_str = "\n".join(holdings_list)

        holdings_value = self.get_holdings_value()
        total_value = self.get_total_value()

        return f"""--- Portfolio ---
Cash: ${self.cash:,.2f}
Holdings Value: ${holdings_value:,.2f}
Total Value: ${total_value:,.2f}

Holdings:
{holdings_str}
-----------------"""

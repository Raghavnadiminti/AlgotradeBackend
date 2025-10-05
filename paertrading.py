class LivePaperTrader:
    def __init__(self, initial_cash=10000):
        self.cash = initial_cash
        self.position = 0.0
        self.avg_price = 0.0
        self.portfolio = initial_cash
        self.trade_log = []


    def on_signal(self, price, signal, timestamp=None):
        """Process new signal from your strategy."""
        
        # BUY signal
        if signal == 1 and self.position == 0:
            self.position = self.cash / price
            self.avg_price = price
            self.cash = 0
            self.trade_log.append((timestamp, "BUY", price))
            print(f"BUY at {price:.2f}")

        # SELL signal
        elif signal == -1 and self.position > 0:
            revenue = self.position * price
            profit = revenue - (self.position * self.avg_price)
            self.cash += revenue
            self.position = 0
            self.trade_log.append((timestamp, "SELL", price, profit))
            print(f"SELL at {price:.2f} | Profit: {profit:.2f}")

        # Update portfolio value every time
        self.portfolio = self.cash + self.position * price

    def summary(self):
        return {
            "cash": self.cash,
            "position": self.position,
            "avg_price": self.avg_price,
            "portfolio": self.portfolio,
            "n_trades": len(self.trade_log),
        }

import yfinance as yf

def get_spot(symbol: str) -> float:
    data = yf.Ticker(symbol)
    return float(data.history(period="1d")["Close"][-1])

def get_india_vix() -> float:
    vix = yf.Ticker("^INDIAVIX")
    return float(vix.history(period="1d")["Close"][-1])

def generate_strikes(spot: float, step: int = 50, count: int = 10):
    atm = round(spot / step) * step
    return [atm + i * step for i in range(-count, count + 1)]


import math
from scipy.stats import norm

RISK_FREE_RATE = 0.0525

def bs_price(S, K, T, sigma, r=RISK_FREE_RATE):
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)

    call = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    put = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    return {
        "call": round(call, 2),
        "put": round(put, 2),
        "delta_call": round(norm.cdf(d1), 3),
        "delta_put": round(norm.cdf(d1) - 1, 3)
    }

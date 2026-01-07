import pytz
from fastapi import FastAPI,WebSocket
from datetime import datetime, time
from app.market_data import get_india_vix
from app.black_scholes import bs_price
from app.schemas import OptionRequest,VixScenarioRequest,VixScenarioRequest1
import pytz, asyncio

IST = pytz.timezone("Asia/Kolkata")
app = FastAPI(title="Option Pricing Engine")

@app.post("/option-chain")
def option_chain(req: OptionRequest):

    india_vix = get_india_vix()
    volatility = india_vix / 100

    expiry_date = datetime.combine(
        datetime.strptime(req.expiry, "%Y-%m-%d").date(),
        time(15, 30)
    )
    expiry_date = IST.localize(expiry_date)
    now_ist = datetime.now(IST)

    seconds = (expiry_date - now_ist).total_seconds()
    if seconds <= 0:
        return {"error": "Option expired"}

    T = max(seconds / (365 * 24 * 60 * 60), 1 / 365)

  
    chain = []
    for spot in req.spot_range:
        price = bs_price(
            S=spot,
            K=req.strike,
            T=T,
            sigma=volatility
        )

        chain.append({
            "spot": spot,
            "call": price["call"],
            "put": price["put"],
            "delta_call": price["delta_call"],
            "delta_put": price["delta_put"]
        })

    return {
        "symbol": req.symbol,
        "strike": req.strike,
        "expiry": req.expiry,
        "india_vix": round(india_vix, 2),
        "volatility_used": round(volatility, 4),
        "pricing_by_spot": chain
    }
    
@app.post("/option-chain/vix-scenarios")
def option_chain_vix_scenarios(req: VixScenarioRequest):

    expiry_date = datetime.combine(
        datetime.strptime(req.expiry, "%Y-%m-%d").date(),
        time(15, 30)
    )
    expiry_date = IST.localize(expiry_date)
    now_ist = datetime.now(IST)

    seconds = (expiry_date - now_ist).total_seconds()
    if seconds <= 0:
        return {"error": "Option expired"}

    T = max(seconds / (365 * 24 * 60 * 60), 1 / 365)

    vix_blocks = []

    for vix in req.vix_range:
        sigma = vix / 100

        spot_prices = []
        for spot in req.spot_range:
            price = bs_price(
                S=spot,
                K=req.strike,
                T=T,
                sigma=sigma
            )

            spot_prices.append({
                "spot": spot,
                "call": price["call"],
                "put": price["put"],
                "delta_call": price["delta_call"],
                "delta_put": price["delta_put"]
            })

        vix_blocks.append({
            "vix": vix,
            "volatility_used": round(sigma, 4),
            "prices": spot_prices
        })

    return {
        "symbol": req.symbol,
        "strike": req.strike,
        "expiry": req.expiry,
        "scenarios": vix_blocks
    }
    
@app.websocket("/ws/option-chain/live-vix")
async def option_chain_live_vix(ws: WebSocket):
    await ws.accept()

  
    req_data = await ws.receive_json()
    req = VixScenarioRequest1(**req_data)

 
    

    try:
        while True:
            expiry_date = datetime.combine(
        datetime.strptime(req.expiry, "%Y-%m-%d").date(),
        time(15, 30)
    )
            expiry_date = IST.localize(expiry_date)
            now_ist = datetime.now(IST)
            seconds = (expiry_date - now_ist).total_seconds()

            if seconds <= 0:
                await ws.send_json({"error": "Option expired"})
                break

            T = max(seconds / (365 * 24 * 60 * 60), 1 / 365)

           
            vix = get_india_vix()
            sigma = vix / 100

         
            prices = []
            for spot in req.spot_range:
                price = bs_price(
                    S=spot,
                    K=req.strike,
                    T=T,
                    sigma=sigma
                )

                prices.append({
                    "spot": spot,
                    "call": price["call"],
                    "put": price["put"],
                    "delta_call": price["delta_call"],
                    "delta_put": price["delta_put"]
                })

           
            await ws.send_json({
                "symbol": req.symbol,
                "strike": req.strike,
                "expiry": req.expiry,
                "days_to_expiry": round(seconds / 86400, 4),
                "vix": vix,
                "volatility_used": round(sigma, 4),
                "prices": prices,
                "timestamp": datetime.now(IST).isoformat()
            })

           
            await asyncio.sleep(5)

    except Exception:
        await ws.close()


    
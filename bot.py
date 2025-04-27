import os, time, base64, requests, schedule
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
print("🚀 Bot starting …", flush=True)

KEY_ID = os.getenv("KALSHI_KEY_ID")
RAW    = os.getenv("KALSHI_PRIVATE_KEY")
if "\\n" in RAW:                       # convert \n escapes if needed
    RAW = RAW.replace("\\n", "\n")

PRIVATE = serialization.load_pem_private_key(RAW.encode(), password=None)
BASE = "https://api.elections.kalshi.com"
   # prod host: https://api.elections.kalshi.com

def _sig(ts, m, p):
    msg = f"{ts}{m}{p}".encode()
    sig = PRIVATE.sign(
        msg,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.DIGEST_LENGTH),
        hashes.SHA256()
    )
    return base64.b64encode(sig).decode()

def _hdr(m, p):
    ts = str(int(time.time()*1000))
    return {
        "KALSHI-ACCESS-KEY": KEY_ID,
        "KALSHI-ACCESS-TIMESTAMP": ts,
        "KALSHI-ACCESS-SIGNATURE": _sig(ts, m, p),
        "Content-Type": "application/json",
    }

def check():
    path = "/trade-api/v2/portfolio/balance"
    r = requests.get(BASE+path, headers=_hdr("GET", path))
    print(time.strftime("%X"), r.status_code, r.text)

schedule.every(1).minutes.do(check)
check()
while True:
    schedule.run_pending()
    time.sleep(1)

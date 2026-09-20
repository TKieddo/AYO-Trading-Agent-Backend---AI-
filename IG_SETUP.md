# IG Markets Demo Setup (Forex / CFDs)

Wire the AYO bot to **IG demo** for forex (and other CFDs). Watch fills in the IG platform UI.

## 1. What you need from IG

1. Demo account (OK while live approval is pending)
2. API key: IG web → **My Account** → **Settings** → **API keys** → create a **demo** key  
   Docs: [labs.ig.com](https://labs.ig.com/) · [sample apps](https://labs.ig.com/sample-apps.html)
3. **Username + password** — same values the IG Labs samples ask for (`Username` / `IG client login name`, not email)

Official samples ([JS](https://github.com/IG-Group/ig-webapi-javascript-sample), [Java](https://github.com/IG-Group/ig-webapi-java-sample)) all do:

- Base URL: `https://demo-api.ig.com/gateway/deal`
- `POST /session` **Version 2**
- Body: `identifier`, `password`, `encryptedPassword: true`
- Password encrypted via `GET /session/encryptionKey` + RSA (this bot matches that)

IG’s API rejects email-shaped identifiers (`validation.pattern.invalid…identifier`). Use the client **username** shown on the login / My IG screens.

## 2. Create `.env` (exact name — not `.env.`)

```bash
EXCHANGE=ig
IG_DEMO=true
IG_API_KEY=your_api_key
IG_USERNAME=your_demo_username
IG_PASSWORD=your_demo_password
# Optional if you have multiple accounts:
# IG_ACCOUNT_ID=XXXXX

# Start small for testing
FOREX_ASSETS=EURUSD GBPUSD
INTERVAL=15m
IG_FIXED_SIZE=1
DEFAULT_LEVERAGE=20
MARGIN_PER_POSITION=100
POSITION_SIZING_MODE=margin
AGENT_MANAGE_EXITS=true
ENABLE_STOP_LOSS_ORDERS=true
TRADING_ENABLED=true

DEEPSEEK_API_KEY=your_deepseek_key
```

Optional epic overrides if search fails in your region:

```bash
IG_EPIC_MAP=EURUSD:CS.D.EURUSD.MINI.IP,GBPUSD:CS.D.GBPUSD.MINI.IP
```

## 3. Smoke-test login (no full bot)

```bash
cd "AYO-Trading-Agent-Backend---AI--main"
python -c "
from src.trading.ig_api import IGAPI
import asyncio
ig = IGAPI()
async def t():
    s = await ig.get_user_state()
    print('balance', s.get('balance'), 'positions', len(s.get('positions', [])))
    px = await ig.get_current_price('EURUSD')
    print('EURUSD', px)
asyncio.run(t())
"
```

## 4. Run the bot

```bash
python -m src.main
```

Look for:

```text
✅ Using IG Markets (DEMO) for forex/CFDs
💰 Account Balance / Buying Power: ...
```

## 5. How you know it traded

| Place | What to check |
|--------|----------------|
| **IG demo platform / website** | Open positions, history, orders |
| **Bot logs** | `IG BUY EURUSD`, `IG closed ...` |
| **`diary.jsonl`** | Entry/exit records |

IG has a real UI — use that as your “exchange screen.”

## 6. Important

- **Forex/CFDs**, not Alpaca-style US share custody
- Leverage is **IG product/account** based — `IG_LEVERAGE` is mainly for sizing/ROI hints
- Use `IG_FIXED_SIZE=1` first so size is predictable on demo
- Keep `IG_DEMO=true` until you’re approved and ready for live
- File must be named **`.env`**

## 7. Stock CFDs on IG

You can add names IG lists in your region (search in platform). Prefer mapping via `IG_EPIC_MAP` for non-FX underlyings.

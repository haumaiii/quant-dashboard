import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

today = datetime.now(ZoneInfo("Asia/Taipei"))
month_index = today.year * 12 + today.month - 1
closes = {}
for offset in range(3, -1, -1):
    year, month = divmod(month_index - offset, 12)
    query = urlencode({"response": "json", "date": f"{year}{month + 1:02}01", "stockNo": "0050"})
    url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY?" + query
    with urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=25) as response:
        report = json.load(response)
    if not report.get("data"):
        if offset == 0:
            continue
        raise RuntimeError(f"Missing TWSE data for {year}-{month + 1:02}")
    for row in report["data"]:
        if not re.fullmatch(r"[\d,.]+", row[6]):
            continue
        roc, mm, dd = map(int, row[0].split("/"))
        closes[f"{roc + 1911:04}-{mm:02}-{dd:02}"] = float(row[6].replace(",", ""))
if len(closes) < 40:
    raise RuntimeError("Insufficient TWSE closing prices")
latest = sorted(closes.items())[-60:]
Path("0050-closes.json").write_text(json.dumps(latest), encoding="utf-8")

import os
import re
import subprocess
import time
import json
from datetime import datetime

CHROME_PATH = "/usr/bin/google-chrome"

def detect_chrome_major_version(chrome_path: str) -> int:
    output = subprocess.check_output([chrome_path, "--version"], text=True)
    match = re.search(r"(\d+)\.", output)
    if not match:
        raise RuntimeError(f"Could not parse Chrome version from: {output!r}")
    return int(match.group(1))

from dotenv import load_dotenv
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import mysql.connector

load_dotenv()

db_host = os.environ["DB_HOST"]
db_port = int(os.environ.get("DB_PORT", 3306))
db_user = os.environ["DB_USER"]
db_password = os.environ["DB_PASSWORD"]
db_name = os.environ["DB_NAME"]

conn = mysql.connector.connect(
    host=db_host,
    port=db_port,
    user=db_user,
    password=db_password,
    database=db_name,
    use_pure=True,
)
cursor = conn.cursor()
cursor.execute("SET SESSION sql_mode = ''")

cursor.execute("SELECT EmitCode, ScrapDay FROM saham_scrap_setting WHERE Status='active'")
settings = cursor.fetchall()

options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--password-store=basic")
options.add_argument("--use-mock-keychain")
driver = uc.Chrome(
    options=options,
    headless=False,
    browser_executable_path=CHROME_PATH,
    version_main=detect_chrome_major_version(CHROME_PATH),
)

try:
    for EmitCode, ScrapDay in settings:
        url = (
            f"https://idx.co.id/primary/ListedCompany/GetTradingInfoSS"
            f"?code={EmitCode}&start=0&length={ScrapDay}"
        )
        driver.get(url)

        json_string = driver.find_element(By.TAG_NAME, "pre").get_attribute("textContent")
        data = json.loads(json_string)

        for row in data["replies"]:
            date = datetime.strptime(row["Date"], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
            delisting_date = row["DelistingDate"] or "0000-00-00"
            values = (
                row["StockCode"], date,
                row["Previous"], row["OpenPrice"], row["FirstTrade"],
                row["High"], row["Low"], row["Close"], row["Change"],
                row["Volume"], row["Value"], row["Frequency"], row["IndexIndividual"],
                row["Offer"], row["OfferVolume"], row["Bid"], row["BidVolume"],
                row["ListedShares"], row["TradebleShares"], row["WeightForIndex"],
                row["ForeignSell"], row["ForeignBuy"], delisting_date,
                row["NonRegularVolume"], row["NonRegularValue"], row["NonRegularFrequency"],
            )
            cursor.execute("""
                INSERT IGNORE INTO saham_historical
                    (EmitCode, `Date`,
                     `Previous`, OpenPrice, FirstTrade,
                     High, Low, `Close`, `Change`,
                     Volume, `Value`, Frequency, IndexIndividual,
                     Offer, OfferVolume, Bid, BidVolume,
                     ListedShares, TradebleShares, WeightForIndex,
                     ForeignSell, ForeignBuy, DelistingDate,
                     NonRegularVolume, NonRegularValue, NonRegularFrequency,
                     DateGenerated)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            """, values)
        conn.commit()

        print(f"Finish Scrap for {EmitCode}")
        time.sleep(3)
finally:
    driver.quit()
    cursor.close()
    conn.close()

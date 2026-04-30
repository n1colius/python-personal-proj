import os
import time
import json
import sys
from datetime import datetime

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import sshtunnel
import mysql.connector

load_dotenv()

ssh_host = os.environ["SSH_HOST"]
ssh_port = int(os.environ["SSH_PORT"])
ssh_username = os.environ["SSH_USERNAME"]
ssh_password = os.environ["SSH_PASSWORD"]

db_host = os.environ["DB_HOST"]
db_user = os.environ["DB_USER"]
db_password = os.environ["DB_PASSWORD"]
db_name = os.environ["DB_NAME"]

with sshtunnel.SSHTunnelForwarder(
    (ssh_host, ssh_port),
    ssh_username=ssh_username,
    ssh_password=ssh_password,
    remote_bind_address=(db_host, 3306),
    allow_agent=False
) as tunnel:
    tunnel.start()

    conn = mysql.connector.connect(
        host="localhost",
        user=db_user,
        password=db_password,
        database=db_name,
        port=tunnel.local_bind_port,
        use_pure=True
    )
    cursor = conn.cursor()

    cursor.execute("SELECT EmitmenCode, ScrapDay FROM scrap_saham_setting WHERE Status='active'")
    settings = cursor.fetchall()

    service = Service()
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)

    for emitmen_code, scrap_day in settings:
        url = (
            f"https://idx.co.id/primary/ListedCompany/GetTradingInfoSS"
            f"?code={emitmen_code}&start=0&length={scrap_day}"
        )
        driver.get(url)

        json_string = driver.find_element(By.TAG_NAME, "pre").get_attribute("textContent")
        data = json.loads(json_string)

        for row in data["replies"]:
            date = datetime.strptime(row["Date"], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
            values = (
                row["StockCode"], date,
                row["Previous"], row["Close"], row["High"], row["Low"],
                row["ListedShares"], row["BidVolume"], row["OfferVolume"], row["Change"],
                row["Volume"], row["Value"], row["Frequency"], row["IndexIndividual"],
                row["Offer"], row["Bid"],
                row["ForeignSell"], row["ForeignBuy"],
                row["NonRegularVolume"], row["NonRegularValue"], row["NonRegularFrequency"],
            )
            cursor.execute("""
                INSERT IGNORE INTO saham_historical
                    (EmitCode, `Date`, PriceOpen, PriceClosed, PriceHigh, PriceLow,
                     ListedShares, BidVolume, OfferVolume, `Change`, Volume, `Value`,
                     Frequency, IndexIndividual, Offer, Bid,
                     ForeignSell, ForeignBuy,
                     NonRegularVolume, NonRegularValue, NonRegularFrequency, DateGenerated)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            """, values)
            conn.commit()

        print(f"Finish Scrap for {emitmen_code}")
        time.sleep(3)

    driver.quit()
    cursor.close()
    conn.close()

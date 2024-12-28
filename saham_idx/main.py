import time
import json
import sys
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

import sshtunnel
import mysql.connector

# Define SSH tunnel parameters
ssh_host = '1.0.1.1'
ssh_port = 22
ssh_username = 'username'
ssh_password = 'passwordnya'
remote_bind_address = ('localhost', 3306)

# Create and start the SSH tunnel
with sshtunnel.SSHTunnelForwarder(
    (ssh_host, ssh_port),
    ssh_username=ssh_username,
    ssh_password=ssh_password,
    remote_bind_address=remote_bind_address,
    allow_agent=False
) as tunnel:
    tunnel.start()

    # Connect to MySQL using the tunnel
    conn = mysql.connector.connect(
        host='localhost',
        user='usernya',
        password='passnya',
        database='dbnya',
        port=tunnel.local_bind_port,
        use_pure=True
    )
    cursor = conn.cursor()

    # Ambil setting scrap
    query = "SELECT EmitmenCode,ScrapDay FROM scrap_saham_setting a where a.Status='active'"
    cursor.execute(query)
    datas_setting_scrap = cursor.fetchall()

    # define service selenium
    service = Service()
    options = webdriver.ChromeOptions()
    #options.add_argument("--headless")
    #options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=service, options=options)

    for data_setting_scrap in datas_setting_scrap:
        EmitmenCode = data_setting_scrap[0]
        ScrapDay = data_setting_scrap[1]
        UrlScrap = "https://idx.co.id/primary/ListedCompany/GetTradingInfoSS?code="+ EmitmenCode +"&start=0&length="+str(ScrapDay)
        driver.get(UrlScrap)

        json_data_element = driver.find_element(By.TAG_NAME, "pre")
        json_string = json_data_element.get_attribute("textContent")

        data_json = json.loads(json_string)
        for data_json_loop in data_json['replies']:
            date_object = datetime.strptime(data_json_loop['Date'], "%Y-%m-%dT%H:%M:%S")

            #lakukan insert ignore ke mysql disini coy
            data_insert_db = (
                data_json_loop['StockCode'],
                date_object.strftime("%Y-%m-%d"),
                data_json_loop['Previous'],
                data_json_loop['Close'],
                data_json_loop['High'],
                data_json_loop['Low'],
                data_json_loop['ListedShares'],
                data_json_loop['BidVolume'],
                data_json_loop['OfferVolume'],
                data_json_loop['Change'],
                data_json_loop['Volume'],
                data_json_loop['Value'],
                data_json_loop['Frequency'],
                data_json_loop['IndexIndividual'],
                data_json_loop['Offer'],
                data_json_loop['Bid'],
                data_json_loop['ForeignSell'],
                data_json_loop['ForeignBuy'],
                data_json_loop['NonRegularVolume'],
                data_json_loop['NonRegularValue'],
                data_json_loop['NonRegularFrequency']
            )
            #print(data_insert_db)

            insert_query = """
            INSERT IGNORE INTO `saham_historical` 
                (EmitCode,`Date`,PriceOpen,PriceClosed,PriceHigh,PriceLow,ListedShares,BidVolume,OfferVolume,`Change`,Volume,`Value`,
                Frequency,IndexIndividual,Offer,Bid,ForeignSell,ForeignBuy,NonRegularVolume,NonRegularValue,NonRegularFrequency,DateGenerated) 
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            """
            cursor.execute(insert_query, data_insert_db)
            conn.commit()

        #kasih jeda 15 detik setiap kali scrap biar tidak kelihatan ngespam
        print("Finish Scrap for " + EmitmenCode)
        time.sleep(3)

    sys.exit()

    # Close the cursor and connection 
    cursor.close()
    conn.close()
    # Stop the tunnel
    tunnel.stop()

    driver.quit()
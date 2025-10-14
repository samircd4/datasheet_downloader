import requests
from selectolax.parser import HTMLParser
from rich import print
import pandas as pd
import time



headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9,bn;q=0.8",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "cookie": "_pxhd=db98b87888afc6f97a434f93b585461fd42073651d4f1139710c99608c5eab8f:0c687cdb-a86e-11f0-997a-313b809116d8; pxcts=0d6c9b83-a86e-11f0-89e0-d9985522a377; _pxvid=0c687cdb-a86e-11f0-997a-313b809116d8; search=%7B%22id%22%3A%22c204eb30-eb26-43d8-ba20-7c527161ac0e%22%2C%22usage%22%3A%7B%22dailyCount%22%3A1%2C%22lastRequest%22%3A%222025-10-13T19%3A52%3A20.484Z%22%7D%2C%22version%22%3A1.1%7D; sacn=%7B%22token%22%3A%22eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJSZXF1ZXN0SWQiOiI4Yjg5OWQ2Ny1lNDA1LTRkMjUtYTcwZi01MDE5ZTkyZTA3MGUiLCJyZWZyZXNoIjoiTmpNNE9UVTVPRFUxTkRBMU1EWXdOVEE0IiwibmJmIjoxNzYwMzg1MTQwLCJleHAiOjE3NjAzODg3NDAsImlhdCI6MTc2MDM4NTE0MCwiaXNzIjoiaHR0cHM6Ly93d3cuZGlnaWtleS5jb20iLCJhdWQiOiJ1c2VyIn0._cUumYrUj32PirufZlCFEskjmGHmX5-iWW8fzMKsFqU%22%2C%22updated%22%3A1760385140597%7D; TS01173021=01694a1a6eb2a1c5cdb468d865cca35e43f1409cfc1890fe4a512d798550ebdce003bb140e1e5b828124c802c67f7cfa8c5e43f203; TS0f82a39e027=08ddc8ffffab2000a52524555ea1ee74eacd6663eec82c9f4c951265c9ebebdc13dc388e200971be088690228c113000ca8a667eef0f102937f19341dbc4e2d00a95679a3f3c07aae3caac0788a9a791318f11b6b3ab959cb367f21854829487; _evga_eea9=fc05d0978a691f42.; dk_sft_ses=c7e79546-d190-4a4b-9840-14332348441e; dkc_tracker=3692197357766; ping-accept-language=en-UK; digikey_theme=dklt; TS0198bc0d=01c72bed21e74819a513e9702762cff7732de3c48fde6e6014fc1e2fb9ec380290dfaeb9a1e48c50ac51a16748edea720916efca24; TSe14c7dc7027=08a1509f8aab2000e8caa8356901552f053d32f75bd99f58020c5a6d089c889d6d48279f105474c9085b03e870113000936767142ceece47d179abc2b666cf4233a024646588c4b60376b433604e6a556a7cccd43c4906c51809cd523d0ebdb0; TS019f5e6c=01c72bed211b69ae5a369a22ae03d1c453661af578abd2a7083ae901659ed2c6d208b88d18ed7b456a9fd122556032103b59063a79; TSbafe380b027=08a1509f8aab2000333e8099d9ee97c11c6e32d0691039bfe8322094b8e112ed481f4df4a4c506e708690ecc901130009b2947ba0aa75fe0d179abc2b666cf42c011e7d449d1be69ceea8cb9e490bb81434ea4ef67ece7d0cb9d1ccf57423dde; TS016ca11c=01c72bed21d85f9dd57e43fa7085046a09ece26560a8fa8266adcf6764e83e966ad928d3885b59cd4b32badfe0ead16d61a17914e8; TSc580adf4027=08a1509f8aab200059ba36f9bcfe60cd7f07e091a7ea75c7230a3011fd2508d4bb09deb394fb966808204cb3a711300069ede4fd2da631cfd179abc2b666cf4289cc927c9296bd35069726419a11b103d825c10c11690b0ec34467b58288539f; dk_tagxi=undefined.0.undefined; dk_ref_data_x=ref_page_type=PS&ref_page_sub_type=PD&ref_page_id=PD&ref_page_url=https://www.digikey.co.uk/en/products/detail/texas-instruments/THS7375IPW/2047675&ref_content_search_keywords=undefined; dk_loginid=undefined; _px2=eyJ1IjoiMjFiM2I2MjAtYTg2ZS0xMWYwLTk3NmYtMzNiMTFmZjcyMDgxIiwidiI6IjBjNjg3Y2RiLWE4NmUtMTFmMC05OTdhLTMxM2I4MDkxMTZkOCIsInQiOjE3NjAzODU0NDM2NDcsImgiOiJiYmVmM2U2ODExMDY1ZTUxYzY3Mjc1YThiMzYwYzdhYmJiNjFiMWI2YzM4MDc0NDRkYThjZTY2ZjNkOGI4ODliIn0=; OptanonAlertBoxClosed=2025-10-13T19:54:29.291Z; _ga=GA1.1.1012960405.1760385143; _ga_1TEG8CV4XM=GS2.1.s1760385142$o1$g0$t1760385269$j60$l0$h0; OptanonConsent=isGpcEnabled=0&datestamp=Tue+Oct+14+2025+01%3A54%3A29+GMT%2B0600+(Bangladesh+Standard+Time)&version=202507.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=2d651b0a-c2f3-441e-9bbc-53610d77c122&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0002%3A1%2CC0004%3A1&intType=1; _pxde=c3273b9fca26f1b05361dd662003f1a7c02996d60134fe4b9d8a63dc861078b3:eyJ0aW1lc3RhbXAiOjE3NjAzODUyNzU0MDIsImZfa2IiOjAsImlwY19pZCI6W10sImNncCI6MX0=; _dd_s=rum=2&id=aab2b17c-c7d9-4567-995c-3fd7483e98c9&created=1760385141792&expire=1760386169245",
    "Content-Type": "text/plain"
}


def get_details(url):
    part = {}
    # proxies = {
    #     'http': 'http://samircd4:bZ5uaDO3TyQ3iGI0@proxy.packetstream.io:31112',
    #     'https': 'http://samircd4:bZ5uaDO3TyQ3iGI0@proxy.packetstream.io:31112',
    # }
    response = requests.get(url, headers=headers)
    html = HTMLParser(response.text)
    detail_description = html.css_first('div[track-data="ref_page_event=Copy Expand Description"]').text(strip=True)
    part['detail_description'] = detail_description
    tbl_row = html.css('table#product-attributes tbody tr')
    for row in tbl_row:
        key = row.css_first('td').text(strip=True)
        if key == 'Supplier Device Package':
            part['supplier_device_package'] = row.css_first('td:nth-child(2)').text(strip=True)
            break
    
    # package_name = html.css_first('div.tss-css-tsu9t4-packageName').text(strip=True)
    print(part)
    return part
    


def main():
    df = pd.read_csv('all_parts.csv')
    urls = df.to_dict(orient='records')
    for parts in urls:
        details = get_details(parts['url'])
        parts.update(details)
        print(parts)
        time.sleep(3)
        # input('Next part: ')


if __name__ == '__main__':
    main()
import requests

url = "https://www.digikey.co.uk/en/products/detail/analog-devices-inc/ADAU1701JSTZ/1246074"

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "upgrade-insecure-requests": "1",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    # Keep only essential cookies for a valid browsing session
    "cookie": "_pxhd=db98b87888afc6f97a434f93b585461fd42073651d4f1139710c99608c5eab8f:0c687cdb-a86e-11f0-997a-313b809116d8; _pxvid=0c687cdb-a86e-11f0-997a-313b809116d8; digikey_theme=dklt; OptanonAlertBoxClosed=2025-10-13T19:54:29.291Z"
}

response = requests.get(url, headers=headers)

print(response.status_code)
print(response.text[:2000])  # Print first 2000 chars

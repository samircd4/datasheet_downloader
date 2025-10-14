import requests
from rich import print
import json


def get_product_code(parts_name: str):
    url = "https://wmsc.lcsc.com/ftps/wm/search/v2/global"

    payload = {
        "keyword": parts_name,
        "secondKeyword": "",
        "brandIdList": [],
        "catalogIdList": [],
        "isStock": False,
        "isAsianBrand": False,
        "isDeals": False,
        "isEnvironment": False
    }
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9,bn;q=0.8",
        "content-type": "application/json;charset=UTF-8",
        "origin": "https://www.lcsc.com",
        "referer": "https://www.lcsc.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
    }

    response = requests.post(url, json=payload, headers=headers)

    data = response.json()['result']['productSearchResultVO']['productList']

    for data_item in data:
        product_code = data_item['productCode']
        print(product_code)
        break
    return product_code


def main():
    parts_name = "1N4007"
    product_code = get_product_code(parts_name)
    url = f"https://www.lcsc.com/product-detail/{product_code}.html"
    print(url)

if __name__ == '__main__':
    main()
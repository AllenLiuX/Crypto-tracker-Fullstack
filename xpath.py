from lxml import etree
import requests
import time

url = 'https://www.coindesk.com/price/'
xpath = '/html/body/div/div[2]/main/section/div[2]/div[1]/div/section/div/div[1]/div/section/div[1]/div[1]/div[2]/div/text()'


def get_latest_crypto_price(crypt):
    try:
        response = requests.get(url+crypt)
    except:
        print('failed')
        return False
    selector = etree.HTML(response.text)
    content = selector.xpath(xpath)
    print(content)
    # price = float(response_json['bpi']['USD']['rate'].replace(',', ''))
    # return price


if __name__ == '__main__':
    start_time = time.time()
    get_latest_crypto_price('btc')
    get_latest_crypto_price('eth')
    print('======= Time taken: %f =======' %(time.time() - start_time))
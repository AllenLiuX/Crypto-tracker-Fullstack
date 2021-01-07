import requests
import json
from lxml import etree
import time
import mail
import mongodb as mg

TICKER_API_URL = 'https://api.coindesk.com/v1/bpi/currentprice.json'
coindesk_url = 'https://www.coindesk.com/price/'
xpath = '/html/body/div/div[2]/main/section/div[2]/div[1]/div/section/div/div[1]/div/section/div[1]/div[1]/div[2]/div/text()'



def get_latest_crypto_price(crypt):
    try:
        response = requests.get(coindesk_url+crypt)
    except:
        print('failed')
        return -1
    selector = etree.HTML(response.text)
    content = selector.xpath(xpath)
    price = content[0]
    print(content[0])
    return price


def get_latest_bitcoin_price():
    try:
        response = requests.get(TICKER_API_URL)
        response_json = response.json()
        # js = json.dumps(response_json, sort_keys=True, indent=4, separators=(',', ':'))
        # print(js)
    except:
        print('failed')
        return -1
    price = float(response_json['bpi']['USD']['rate'].replace(',', ''))
    return price


def price_monitor(current_price, raise_line, drop_line, change_interval, user_mails, crypto):
    if current_price > raise_line:  # price raised
        while current_price > raise_line:
            raise_line += change_interval
            drop_line += change_interval
        title = crypto + 'raise report. Price: ' + str(current_price)  # 邮件主题
        content = '<html><body><h1>Hello,</h1><p>Here is your report from <a href="www.vincentliux.com/bitcoin/">www.vincentliux.com/bitcoin/</a></p>' + \
                  '<p>The current bitcoin price is: </p><b style="color: red">' + \
                  str(current_price) + \
                  '</b><p>Your next raise alert line is '+str(raise_line)+', and next drop alert line is '+str(drop_line) +\
                  '.</p><p>If you want to cancel your subscription, visit <a href="www.vincentliux.com/bitcoin-cancel/">www.vincentliux.com/bitcoin-cancel/</a></p>' +\
                  '<p>See more bitcoin info at: <a href="https://www.coindesk.com/price/bitcoin">Bitcoin Info</a>...</p><p>Best wishes,</p><p>--Vincent Liu</p></body></html>'
        # mail.quick_send_email(smtpObj, title, content)
        mail.sendEmail(title, content, user_mails)

    if current_price < drop_line:
        while current_price < drop_line:
            raise_line -= change_interval
            drop_line -= change_interval
        title = crypto + 'drop report. Price: ' + str(current_price)  # 邮件主题
        content = '<html><body><h1>Hello,</h1><p>Here is your report from <a href="www.vincentliux.com/bitcoin/">www.vincentliux.com/bitcoin/</a></p>' + \
                  '<p>The current bitcoin price is: </p><b style="color: red">' + \
                  str(current_price) + \
                  '</b><p>Your next raise alert line is ' + str(raise_line) + ', and next drop alert line is ' + str(drop_line) + \
                  '.</p><p>If you want to cancel your subscription, visit <a href="www.vincentliux.com/bitcoin-cancel/">www.vincentliux.com/bitcoin-cancel/</a></p>' + \
                  '<p>See more bitcoin info at: <a href="https://www.coindesk.com/price/bitcoin">Bitcoin Info</a>...</p><p>Best wishes,</p><p>--Vincent Liu</p></body></html>'
        # content = '<html><body><h1>Hello,</h1>' + \
        #           '<p>See more bitcoin info at: <a href="https://coinmarketcap.com/zh/currencies/bitcoin/">Bitcoin Info</a>...</p><p>The current bitcoin price is: </p>' + \
        #           str(current_price) + '</body></html>'
        # mail.quick_send_email(smtpObj, title, content)
        mail.sendEmail(title, content, user_mails)
    print('current price: ', current_price)
    print('raise line: ', raise_line)
    print('drop line: ', drop_line)
    return raise_line, drop_line


def set_mg(user_mail, raise_line, change_interval, crypto):
    name_mapping = {'btc': 'btc', 'BTC': 'btc', 'bitcoin': 'btc', 'Bitcoin': 'btc', 'eth': 'eth', 'ETH': 'eth',
                    'etc': 'etc', 'stellar': 'stellar'}
    if crypto in name_mapping:
        crypto = name_mapping[crypto]
    info = {'user_mail': user_mail,
            'raise_line': raise_line,
            'change_interval': change_interval,
            'crypto': crypto,
    }
    try:
        mg.show_datas('interval_info', {'user_mail': user_mail, 'crypto': crypto}, 'Bitcoin')[0]
        mg.delete_datas({'user_mail': user_mail}, 'interval_info', 'Bitcoin')
    except:
        pass
    try:
        mg.insert_data(info, collection='interval_info', db='Bitcoin')
    except:
        return False
    return True


def get_mg(user_mail, crypto):
    data = mg.show_datas('interval_info', {'user_mail': user_mail, 'crypto': crypto}, 'Bitcoin')[0]
    return data['raise_line'], data['change_interval']


def remove_mg(user_mail, crypto):
    try:
        mg.delete_datas({'user_mail': user_mail, 'crypto': crypto}, 'interval_info', 'Bitcoin')
    except:
        print('failed')
        return False
    return True


def one_alert(user_mail, crypto):
    raise_line, change_interval = get_mg(user_mail, crypto)
    user_mails = [user_mail]
    drop_line = raise_line - change_interval
    while True:
        raise_line, drop_line = price_monitor(crypto, raise_line, drop_line, 300, user_mails)
        time.sleep(20)


def multiple_alert():
    datas = mg.show_datas('interval_info', {}, 'Bitcoin')
    cryptos = ['eth', 'etc', 'stellar']
    while True:
        prices = {}
        prices['btc'] = get_latest_bitcoin_price()
        for crypto in cryptos:
            prices[crypto] = get_latest_crypto_price(crypto)
        for data in datas:
            user_mail, raise_line, change_interval, crypto = data['user_mail'], data['raise_line'], data['change_interval'], data['crypto']
            print('----For ' + user_mail + '-------')
            user_mails = [user_mail]
            drop_line = raise_line - change_interval
            if crypto not in cryptos:
                cryptos.append(crypto)
                continue
            raise_line, drop_line = price_monitor(prices[crypto], raise_line, drop_line, change_interval, user_mails, crypto)
            set_mg(user_mail, raise_line, change_interval, crypto)
        time.sleep(30)


if __name__ == '__main__':
    start_time = time.time()
    # raise_line = 34900
    # change_interval = 300
    # user_mail = 'allenliux01@163.com'
    # crypto = 'btc'
    # set_mg(user_mail, raise_line, change_interval, crypto)
    # one_alert(user_mail, crypto)
    multiple_alert()
    print('======= Time taken: %f =======' %(time.time() - start_time))
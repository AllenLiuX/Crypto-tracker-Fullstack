import requests
import json
import time
import mail
import mongodb as mg

TICKER_API_URL = 'https://api.coindesk.com/v1/bpi/currentprice.json'

def get_latest_crypto_price():
    try:
        response = requests.get(TICKER_API_URL)
        response_json = response.json()
        # js = json.dumps(response_json, sort_keys=True, indent=4, separators=(',', ':'))
        # print(js)
    except:
        print('failed')
    price = float(response_json['bpi']['USD']['rate'].replace(',', ''))
    return price


def price_monitor(raise_line, drop_line, change_interval, user_mail):
    current_price = get_latest_crypto_price()
    if current_price > raise_line:  # price raised
        while current_price > raise_line:
            raise_line += change_interval
            drop_line += change_interval
        title = 'bitcoin raise report. Price: ' + str(current_price)  # 邮件主题
        content = '<html><body><h1>Hello,</h1>' + \
                  '<p>See more bitcoin info at: <a href="https://www.coindesk.com/price/bitcoin">Bitcoin Info</a>...</p><p>The current bitcoin price is: </p>' + \
                  str(current_price) + '</body></html>'
        # mail.quick_send_email(smtpObj, title, content)
        mail.sendEmail(title, content)

    if current_price < drop_line:
        while current_price < drop_line:
            raise_line -= change_interval
            drop_line -= change_interval
        title = 'bitcoin drop report. Price: ' + str(current_price)  # 邮件主题
        content = '<html><body><h1>Hello,</h1>' + \
                  '<p>See more bitcoin info at: <a href="https://coinmarketcap.com/zh/currencies/bitcoin/">Bitcoin Info</a>...</p><p>The current bitcoin price is: </p>' + \
                  str(current_price) + '</body></html>'
        # mail.quick_send_email(smtpObj, title, content)
        mail.sendEmail(title, content, [user_mail])
    print('current price: ', current_price)
    print('raise line: ', raise_line)
    print('drop line: ', drop_line)
    return raise_line, drop_line


def set_mg(user_mail, raise_line, change_interval):
    info = {'user_mail': user_mail,
            'raise_line': raise_line,
            'change_interval': change_interval
    }
    try:
        mg.show_datas('interval_info', {'user_mail': user_mail}, 'Bitcoin')[0]
        mg.delete_datas({'user_mail': user_mail}, 'interval_info', 'Bitcoin')
    except:
        pass
    mg.insert_data(info, collection='interval_info', db='Bitcoin')


def get_mg(user_mail):
    data = mg.show_datas('interval_info', {'user_mail': user_mail}, 'Bitcoin')[0]
    return data['raise_line'], data['change_interval']


if __name__ == '__main__':
    start_time = time.time()
    raise_line = 34900
    change_interval = 300
    user_mail = 'allenliux01@163.com'
    set_mg(user_mail, raise_line, change_interval)
    raise_line, change_interval = get_mg(user_mail)
    drop_line = raise_line-change_interval
    while True:
        raise_line, drop_line = price_monitor(raise_line, drop_line, 300, [user_mail])
        time.sleep(30)
    print('======= Time taken: %f =======' %(time.time() - start_time))
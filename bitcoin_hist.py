import numpy as np
import pandas as pd
import requests
import json
import time
import seaborn as sns
import matplotlib.pyplot as plt
url = 'https://api.blockchain.info/charts/market-price?timespan=2weeks&rollingAverage=8hours&format=json'


def get_bitcoin_prices(crypto):
    try:
        response = requests.get(url)
        response_json = response.json()
        js = json.dumps(response_json, sort_keys=True, indent=4, separators=(',', ':'))
    except:
        print('failed')
        return False
    print(js)
    print(response_json['values'])
    df = pd.DataFrame(response_json['values'])
    # df['time'] = df['x'].apply(time.strftime("%Y-%m-%d %H:%M:%S", df['x']), axis=1)
    df['time'] = df['x'].apply(lambda x: time.ctime(x))
    print(df)
    plt.figure(figsize=(15, 8))
    sns.lineplot(df['x'], df['y'])
    plt.tick_params(axis='x', labelsize=8)  # 设置x轴标签大小
    plt.xticks(ticks=df['x'], labels=df['time'], rotation=-25)
    plt.show()
    return js
    # return response_json['bpi']['USD']['rate']


if __name__ == '__main__':
    start_time = time.time()
    current_price = get_bitcoin_prices('bitcoin')
    # print(current_price)
    print('======= Time taken: %f =======' %(time.time() - start_time))
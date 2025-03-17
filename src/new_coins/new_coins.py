# new_coins/new_coins.py

import requests
import json
from datetime import datetime, timedelta, timezone


def get_new_coins():
    url = 'https://advanced-api-v2.pump.fun/coins/list?sortBy=creationTime'

    headers = {
        'authority': 'advanced-api-v2.pump.fun',
        'method': 'GET',
        'path': '/coins/list?sortBy=creationTime',
        'scheme': 'https',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
        'referer': 'https://pump.fun/'
    }

    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    coins = []

    for coin in data:
        timestamp_ms = coin['creationTime']
        timestamp = timestamp_ms//1000
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        current_time = datetime.now(timezone.utc)
        age = current_time - dt

        coin_info = {
            'image': coin['imageUrl'],
            'name': coin['name'],
            'ticker': coin['ticker'],
            'age': timestamp,
            'market_cap': coin['marketCap'],
            'holders': coin['numHolders'],
            'volume': coin['volume'],
            'dev': coin['dev'],
            'address': coin['coinMint'],
            'red_flag': False
        }

        for holder in coin['holders']:
            if holder['holderId'] == coin_info['dev']:
                if holder['ownedPercentage'] > 5:
                    coin_info['red_flag'] = True

            if holder['ownedPercentage'] < 20:
                coin_info['red_flag'] = True


        if coin_info['volume'] < (coin_info['market_cap'] * .05):
            coin_info['red_flag'] = True

        if coin_info['holders'] < 5:
            coin_info['red_flag'] = True


        coins.append(coin_info)

    return coins

def get_almost_graduated_coins():
    url = 'https://advanced-api-v2.pump.fun/coins/about-to-graduate'

    headers = {
        'authority': 'advanced-api-v2.pump.fun',
        'method': 'GET',
        'path': '/coins/about-to-graduate',
        'scheme': 'https',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
        'referer': 'https://pump.fun/'
    }

    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    coins = []

    for coin in data:
        timestamp_ms = coin['creationTime']
        timestamp = timestamp_ms / 1000
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        current_time = datetime.now(timezone.utc)
        age = current_time - dt


        coin_info = {
            'address': coin['coinMint'],
            'name': coin['name'],
            'ticker': coin['ticker'],
            'volume': coin['volume'],
            'market_cap': coin['marketCap'],
            'image': coin['imageUrl'],
            'holders': coin['numHolders'],
            'age': timestamp,
            'bonding_curve': coin['bondingCurveProgress'],
        }

        coins.append(coin_info)

    return coins


if __name__ == '__main__':
    print(get_almost_graduated_coins())
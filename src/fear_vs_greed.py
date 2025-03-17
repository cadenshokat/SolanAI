import requests
import json


def get_fear_vs_greed():
    url = "https://pro-api.coinmarketcap.com/v3/fear-and-greed/latest"

    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': 'ebd58352-7590-43d6-b14f-9bc2de65eab1',
    }

    response = requests.get(url, headers=headers)

    data = json.loads(response.text)
    drill = data.get('data')

    d = {
        "value": drill.get('value'),
        "name": drill.get('value_classification')
    }

    return d


def get_fear_vs_greed_historical():
    url = "https://pro-api.coinmarketcap.com/v3/fear-and-greed/historical"

    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': 'ebd58352-7590-43d6-b14f-9bc2de65eab1',
    }

    response = requests.get(url, headers=headers)

    r = json.loads(response.text)
    data = r.get('data')

    trendline = {}
    for d in data:
        trendline[d.get('timestamp')] = d.get('value')


    return trendline


if __name__ == '__main__':
    get_fear_vs_greed_historical()
import requests


def format_market_cap(number):
    num = int(number)
    if num < 1000:
        return f"{num:,}"  # e.g., 6,392
    elif num < 1_000_000:
        formatted = f"{num/1000:.2f}".rstrip('0').rstrip('.')
        return f"{formatted}k"  # e.g., 435.49k
    elif num < 1_000_000_000:
        formatted = f"{num/1_000_000:.2f}".rstrip('0').rstrip('.')
        return f"{formatted}m"  # e.g., 4.39m
    elif num < 1_000_000_000_000:
        formatted = f"{num/1_000_000_000:.2f}".rstrip('0').rstrip('.')
        return f"{formatted}b"  # e.g., 1.23b
    else:
        formatted = f"{num/1_000_000_000_000:.2f}".rstrip('0').rstrip('.')
        return f"{formatted}t"  # e.g., 0.98t



def get_coin_data(address):
    url = f"https://api.coingecko.com/api/v3/coins/solana/contract/{address}"

    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": "CG-ixkya7gsfEXo4ha6ueFBFNS5\t"
    }

    response = requests.get(url, headers=headers)
    data = response.json()
    image = data.get("image",[]).get("thumb")
    market_cap = data.get("market_data", {}).get("market_cap",[]).get("usd", 0)
    twitter_followers = data.get("community_data").get("twitter_followers", 0)
    mkt_cap = format_market_cap(market_cap)

    coin_info = {
        'image': image,
        'name': data['name'],
        'ticker': data['symbol'],
        'market_cap': mkt_cap,
        'twitter_followers': twitter_followers,
    }

    return coin_info





def get_multiple_coin_data(addresses):
    addresses_str = ",".join(addresses)
    print(addresses_str)
    response = requests.get(f"https://api.dexscreener.com/tokens/v1/solana/{addresses_str}")

    data = response.json()
    coins_data = []

    for coin in data:
        coin_info = coin.get("info", {})
        coin_socials = coin_info.get("socials", [])
        twitter_url = ""
        name = coin.get("baseToken").get("name")
        symbol = coin.get("baseToken").get("symbol")
        age = coin.get("pairCreatedAt")


        for social in coin_socials:
            if social.get("type") == "twitter":
                twitter_url = social.get("url")


        coin_info = {
            'image': coin_info.get('imageUrl'),
            'name': name,
            'ticker': symbol,
            'market_cap': format_market_cap(coin['marketCap']),
            'twitter': twitter_url,
            'age': age,
        }

        coins_data.append(coin_info)

    return coins_data

if __name__ == "__main__":
    adds = ["9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump", "6AJcP7wuLwmRYLBNbi825wgguaPsWzPBEHcHndpRpump", "3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh" ]
    print(get_coin_data("6AJcP7wuLwmRYLBNbi825wgguaPsWzPBEHcHndpRpump"))
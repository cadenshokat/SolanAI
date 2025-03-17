import requests
import json
from collections import defaultdict
from datetime import datetime, timezone, timedelta

# IF 403 ERROR, UPDATE COOKIES


def get_account_info(wallet):
    headers = {
        'authority': 'api-v2.solscan.io',
        'method': 'GET',
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': '_ga=GA1.1.1699418279.1738128545; cf_clearance=5YPMESNKkJSW6kYIssFiYSCGNn2PlCarRj9DplykMIQ-1740254748-1.2.1.1-88izjY5XRNQhBd4ga5OlDbJhnGtrMWjTzDNoSFbAgr3ljr_v4Xo0GrO2inbe_3p5TeRSlgcKGsXMZNVxvjnrdHRGAZOpHCfIoDJaCMAb4Rwdiq4A1rvYeiGaMFCYqcRiXDTNT_QZME4F3scH_BuSTJ3zmy.8FrSjdWivYXt8FcxNHVcTeGH6kEgLstcc0zHE4Zm5DKCTGo3QFVDt21c4.5_jxFAXpRYSejdrv5LUDNWhLe9q9YSnWWvrMSxKXO67PXtTJHnAwqrr6CUGGI5ZEPmeyL9402k5H76p4AeOw7QX7cE4qkoaH8LY4FhkgQMW.lTUuhzCpXHfgxTWc5VPXA; _ga_PS3V7B7KV0=GS1.1.1740253574.37.1.1740254811.0.0.0',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
        'referer': 'https://solscan.io/',
        'origin': 'https://solscan.io',
        'connection': 'keep-alive',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        'sol-Aut': '7EWc8eTDDlaB9dls0fKZ2lMPvyo6npPZ5oSCITEP'
    }

    account_url = f'https://api-v2.solscan.io/v2/account?address={wallet}'
    response = requests.get(account_url, headers=headers)
    print(response)

    data = json.loads(response.text)
    tokens = data['data']

    print(data)
    print(tokens)


def get_recent_transfers(wallets):
    wallet_transfers = {}

    for wallet in wallets:
        headers = {
            'authority': 'api-v2.solscan.io',
            'method': 'GET',
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'cookie': '_ga=GA1.1.1699418279.1738128545; cf_clearance=fzWqmkM7xASSvNzsusnYST3GjmLmqjne9vVV4Th8TfI-1742190541-1.2.1.1-hUFQOIjr8zdee07y0r0cazNqaveMuO5RmQOv4eku6zfugdZdvUP8nLBBuciJziDXuGwttAUcYzZYubfYV7auzBYw1BfItUHAcMZhv_gOmhKy2geQgm3U0qE0GsvvSCGADpv.6kaeq_8CVN_UjAPuHtaz2jzFH1_VyFA0vQryFoDzHiL5Zv3rigxSAPoeeGE912VTGFMGINthbgxUs3Xv.5jq7L4bqbQC3I8OLfU0CWtLbPCTluO2oSfjWf15bRATXtIxFR_c_FAe0j8OoF0B09d_Ebt59MQEffzmzM_Ct1T6ux6NOFPw.y2l45eCDbw65SLK6bJTSvI3yntI003pEAUs.TzcDpZ_vLlmROJnBCfMYHMuyp2MdCvB8ypOx1nbtmI.sgu0cWVMBnHNFyJWSOkup48XuB4.6ByvICxVtfM; _ga_PS3V7B7KV0=GS1.1.1742190542.67.0.1742190542.0.0.0',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
            'referer': 'https://solscan.io/',
            'origin': 'https://solscan.io',
            'connection': 'keep-alive',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
            'sol-Aut': '7EWc8eTDDlaB9dls0fKZ2lMPvyo6npPZ5oSCITEP'
        }


        transactions_url = f'https://api-v2.solscan.io/v2/account/transfer?address={wallet}&page=1&page_size=30&remove_spam=true&exclude_amount_zero=true'
        response = requests.get(transactions_url, headers=headers)

        address = wallet

        data = json.loads(response.text)
        transfer_data = data['data']

        transfers = []


        for transfer in transfer_data:
            # print(transfer)

            if transfer['activity_type'] == 'ACTIVITY_SPL_TRANSFER' and transfer['token_address'] != 'So11111111111111111111111111111111111111111' and transfer['token_address'] != 'So11111111111111111111111111111111111111112' and transfer['token_address'] != 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v':
                transfer_time = transfer['block_time']
                dt = datetime.fromtimestamp(transfer_time, tz=timezone.utc)
                current_time = datetime.now(timezone.utc)
                age = current_time - dt
                amount = transfer['amount']
                decimals = transfer['token_decimals']
                amt = amount / (10 ** decimals)


                transfer_info = {
                    'transaction_id': transfer['trans_id'],
                    'token_address': transfer['token_address'],
                    'amount': amt,
                    'age': str(age),
                    'activity_type': transfer['activity_type'],
                    'block_time': transfer['block_time']
                }

                transfers.append(transfer_info)

        wallet_transfers.update({address: transfers})

    return wallet_transfers


def parse_timedelta(age_str):
    """
    Converts an age string ('0:03:07.102918' or '2 days, 0:12:48.461991') into a timedelta object.
    """
    parts = age_str.split(", ")
    if len(parts) == 2:  # 'X days, HH:MM:SS.microseconds'
        days = int(parts[0].split()[0])
        time_part = parts[1]
    else:  # 'HH:MM:SS.microseconds' (no days)
        days = 0
        time_part = parts[0]

    hours, minutes, seconds = map(float, time_part.split(":"))
    return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)


def get_new_transfers(wallet_transfers):
    new_transfers = {}
    five_minutes_ago = timedelta(minutes=5)  # Define the cutoff

    for wallet, transfers in wallet_transfers.items():
        recent_transactions = []

        for transfer in transfers:
            age = parse_timedelta(transfer['age'])  # Convert 'age' string to timedelta

            if age <= five_minutes_ago:
                recent_transactions.append(transfer)  # Store transfer if within the last 5 minutes

        if recent_transactions:
            new_transfers[wallet] = recent_transactions  # Only add wallet if there are recent transactions

    return new_transfers


def get_popular_tokens(wallet_transfers, min_wallets=2):

    token_counts = defaultdict(int)  # Stores {token: number_of_unique_wallets_that_bought_it}
    token_wallets = defaultdict(set)

    for wallet, transfers in wallet_transfers.items():
        for transfer in transfers:
            token = transfer['token_address']
            token_wallets[token].add(wallet)

    for token, wallets in token_wallets.items():
        token_counts[token] = len(wallets)

    popular_tokens = {token: count for token, count in token_counts.items() if count >= min_wallets}

    return popular_tokens  # Returns {token: num_unique_wallets}


def get_new_popular_tokens(wallet_transfers, min_wallets=2):
    token_counts = defaultdict(int)  # Stores {token: number_of_unique_wallets_that_bought_it}
    token_wallets = defaultdict(set)
    five_minutes_ago = timedelta(minutes=5)  # Define the cutoff


    for wallet, transfers in wallet_transfers.items():
        for transfer in transfers:
            age = parse_timedelta(transfer['age'])  # Convert 'age' string to timedelta

            if age <= five_minutes_ago:
                token = transfer['token_address']
                token_wallets[token].add(wallet)

    for token, wallets in token_wallets.items():
        token_counts[token] = len(wallets)

    popular_tokens = {token: count for token, count in token_counts.items() if count >= min_wallets}

    return popular_tokens  # Returns {token: num_unique_wallets}


def main(wallets, min_wallets):


    recent_transfers = get_recent_transfers(wallets)

    hot_buys = get_popular_tokens(recent_transfers, min_wallets)
    new_hot_buys = get_new_popular_tokens(recent_transfers, min_wallets)
    new_transfers = get_new_transfers(recent_transfers)

    return hot_buys, new_hot_buys, new_transfers


if __name__ == '__main__':
    wallets = ['B1MrFCtevPz8M2XnXyPArEYAjVbYroBMuD2Nn6GHbNrt', 'B1MrFCtevPz8M2XnXyPArEYAjVbYroBMuD2Nn6GHbNrt', 'MfDuWeqSHEqTFVYZ7LoexgAK9dxk7cy4DFJWjWMGVWa',
           '2C5n9nGrWkniwgcN9UZQk16QQU1sPBe9v9Fg9Y9VKmDo', 'FNay34Y1YJ634DHyzgQPTHgqojAirbLKp3uPHTRDwCBn', 'B88xH3Jmhq4WEaiRno2mYmsxV35MmgSY45ZmQnbL8yft',
           'ChGA1Wbh9WN8MDiQ4ggA5PzBspS2Z6QheyaxdVo3XdW6', 'Hm7ZZomcstqbCHsdXPWL9yUpCQCJdKCXinaQZwbvRGtC', 'j1oAbxxiDUWvoHxEDhWE7THLjEkDQW2cSHYn2vttxTF',
           '7MFtwZqXtGWQsrQwygCh2yYDGxN4Csv6YMkbaqMcHfpz', 'BeTvN1ucBnCj4Ef688i51KHn2oq35CWDvD2J5aLFp17t', 'EDozia8CitSkQCnpXu3ekLJCoiLvPUWWLgiRTKiES2j2']

    print(datetime.now())
    print(main(wallets, 3))
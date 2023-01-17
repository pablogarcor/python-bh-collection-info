from web3 import Web3
from dotenv import load_dotenv
import aiohttp
import asyncio
import os
import json

load_dotenv()  # take environment variables from .env.


# This is a sample Python script.

# Press Mayús+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

def get_w3_instance():
    provider = os.environ['HTTPS_PROVIDER_URL']
    print(provider)
    w3 = Web3(Web3.HTTPProvider(provider))
    return w3


def get_bh_contract_instance(w3_instance):
    contract_address = os.environ['BH_CONTRACT_ADDRESS']
    contract_abi_string = os.getenv('BH_CONTRACT_ABI')
    contract_abi = json.loads(contract_abi_string)
    bh_contract = w3_instance.eth.contract(address=contract_address, abi=contract_abi)
    return bh_contract


def find(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return dic['value']
    return -1


async def get_bh(session, url, token_id):
    async with session.get(url) as resp:
        bh_metadata = await resp.json()
        brand_value = find(bh_metadata['attributes'], 'trait_type', 'Brand')
        print(bh_metadata)
        return {'token_id': token_id, 'brand': brand_value}


async def write_brand_to_file():
    async with aiohttp.ClientSession() as session:

        tasks = []
        # 10k iterations to get 10k based heads
        for number in range(1, 10000 + 1):
            url = f'https://drops.api.topdogstudios.io/basedAf/token/{number}'
            tasks.append(asyncio.ensure_future(get_bh(session, url, number)))

        all_bh = await asyncio.gather(*tasks)
        with open('bh_list.txt', 'w') as bh_file:
            for bh in all_bh:
                json.dump(bh, bh_file)
                bh_file.write("\n")


asyncio.run(write_brand_to_file())

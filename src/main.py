from web3 import Web3
from dotenv import load_dotenv
import aiohttp
import asyncio
import os
import json
from collections import defaultdict

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


# asyncio.run(write_brand_to_file())

def get_first_element_of_tuple(n):
    return n[0]


def get_bh_brand_of_line(n):
    json_line = json.loads(n)
    return json_line['brand']


async def get_bh_owners(bh_contract):
    owners = bh_contract.functions.explicitOwnershipsOf(thousand_list).call()
    owners_list = list(map(get_first_element_of_tuple, owners))
    return owners_list


async def get_bh_brands():
    with open('bh_list.txt', 'r') as bh_file:
        lines = bh_file.readlines()
        brands_list = list(map(get_bh_brand_of_line, lines))
        return brands_list


async def get_bh_brands_per_owner_list(contract):
    bh_owner_and_brands_list = []
    bh_owners_brands_results = await asyncio.gather(asyncio.ensure_future(get_bh_brands()),
                                                    asyncio.ensure_future(get_bh_owners(contract)))
    for x in range(0, 9999):
        owner = bh_owners_brands_results[1][x]
        brand = bh_owners_brands_results[0][x]
        bh_owner_and_brands_list.append((owner, brand))

    mapp = defaultdict(list)
    for key, val in bh_owner_and_brands_list:
        mapp[key].append(val)
    res = [(key, *val) for key, val in mapp.items()]
    return res


def get_list_of_sixers(brands_per_owner_list):
    list_of_sixers = []
    check_list=['ランダム Instant Foods', 'Fraz', 'DGAF', 'HedCrank', 'ShitHead', '8008135']
    for brands_per_owner_tuple in brands_per_owner_list:
        if all(t in brands_per_owner_tuple for t in check_list):
            list_of_sixers.append(brands_per_owner_tuple[0])
    return list_of_sixers


if __name__ == '__main__':
    thousand_list = list(range(1, 10000))
    my_w3 = get_w3_instance()
    my_contract = get_bh_contract_instance(my_w3)
    brands_per_user_list = asyncio.run(get_bh_brands_per_owner_list(my_contract))
    list_of_sixers = get_list_of_sixers(brands_per_user_list)
    print(list_of_sixers)
    print(len(list_of_sixers))

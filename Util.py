from os import path, remove
import glob
import random
import shelve

def get_dict(store):
    s = shelve.open(store)

    stocks = s.items()
    stock_dict = convert_tuple_to_dict(stocks)

    s.close()

    return stock_dict

def set_shelf(store, vals):
    s = shelve.open(store)
    s.update(vals)
    s.close()


def clear_shelf(store):
    if path.exists(f"{store}.dat"):
        card_dat_list = glob.glob(f"{store}.*")
        for card_dat in card_dat_list:
            remove(card_dat)

def convert_tuple_to_dict(tup):
    dic = {}
    for a, b in tup:
        dic.setdefault(a, b)

    return dic

def get_random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",  # IE
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36 OPR/72.0.3815.378",  # Opera
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",  # Chrome
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15",  # Safari
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0"  # Firefox
    ]

    return user_agents[random.randint(0, len(user_agents) - 1)]

from API import API
from Item import Item
from requests_html import AsyncHTMLSession
from string import Template
import asyncio
import datetime
import random
import shelve
import sys
import time

import Util
import webbrowser

# Init global temp dict.
global item_set

# Print alert, tweet it if enabled.
def notify_difference(item, original_text):
    print("#######################################")
    print(f"            {item.get_model()} STOCK ALERT           ")
    print(f"           {time.ctime()}")
    print(f"Button has changed from {original_text} to {item.get_button_text()} for {item.get_name()}.")
    if "newegg" in item.get_url():
        print(f"Add it to your cart: https://secure.newegg.com/Shopping/AddToCart.aspx?ItemList={item.get_item_id()}&Submit=ADD&target=NEWEGGCART\n\n")        
        webbrowser.open_new(f"https://secure.newegg.com/Shopping/AddToCart.aspx?ItemList={item.get_item_id()}&Submit=ADD&target=NEWEGGCART")
    print(f"Current price: {item.get_price()}.")
    print(f"Please visit {item.get_url()} for more information.")
    webbrowser.open_new(item.get_url())
    print("#######################################")
    print("")
    print("")

# Build list of URLs to check
async def get_stock():
    bestbuy_base_url = "https://www.bestbuy.com/site/computer-items-components/video-graphics-items/abcat0507002.c?id=abcat0507002"
    bh_base_url = "https://www.bhphotovideo.com/c/products/Graphic-Cards/ci/6567/N/3668461602"
    amd_base_url = "https://www.amd.com/en/direct-buy/us"
    bh_rtx_model_stub = Template("?filters=fct_nvidia-geforce-series_5011%3Ageforce-rtx-$Model")
    bestbuy_rtx_model_stub = Template("qp=gpusv_facet%3DGraphics%20Processing%20Unit%20(GPU)~NVIDIA%20GeForce%20RTX%20$Model")
    bestbuy_radeon_model_stub = Template("qp=gpusv_facet%3DGraphics%20Processing%20Unit%20(GPU)~AMD%20Radeon%20RX%20$Model")

    # Get the current time and append to the end of the url just to add some minor difference
    # between scrapes.
    t = int(round(time.time() * 1000))

    urls = {
        # GPUs
        f"3070-={bestbuy_base_url}&{bestbuy_rtx_model_stub.substitute(Model='3070')}&t={t}",
        f"3070-=https://www.newegg.com/p/pl?N=100007709%20601357250&PageSize=96&t={t}",
        f"3070-={bh_base_url}{bh_rtx_model_stub.substitute(Model='3070')}&t={t}",
        f"3080-={bestbuy_base_url}&{bestbuy_rtx_model_stub.substitute(Model='3080')}&t={t}",
        f"3080-=https://www.newegg.com/p/pl?N=100007709%20601357247&PageSize=96&t={t}",
        f"3080-={bh_base_url}{bh_rtx_model_stub.substitute(Model='3080')}&t={t}",
        f"3090-={bestbuy_base_url}&{bestbuy_rtx_model_stub.substitute(Model='3090')}&t={t}",
        f"3090-=https://www.newegg.com/p/pl?N=100007709%20601357248&PageSize=96&t={t}",
        f"6800-={bestbuy_base_url}&{bestbuy_radeon_model_stub.substitute(Model='6800')}&t={t}",
        f"6800-=https://www.newegg.com/p/pl?N=100007709%20601359427&PageSize=96&t={t}",
        f"6800 XT-={bestbuy_base_url}&{bestbuy_radeon_model_stub.substitute(Model='6800%20XT')}&t={t}",
        f"6800 XT-=https://www.newegg.com/p/pl?N=100007709%20601359422&PageSize=96&t={t}",
        f"6900 XT-={bestbuy_base_url}&{bestbuy_radeon_model_stub.substitute(Model='6900%20XT')}&t={t}",
        f"6900 XT-=https://www.newegg.com/p/pl?N=100007709%20601359957&PageSize=96&t={t}",        
        # CPUs
        f"Ryzen-=https://www.bestbuy.com/site/promo/ryzen-5000-cpu",
        f"Ryzen-=https://www.newegg.com/p/pl?N=100007671%2050001028%20601359163&t={t}"
        # Consoles
        f"PS5-=https://www.bestbuy.com/site/playstation-5/ps5-consoles/pcmcat1587395025973.c?id=pcmcat1587395025973",
        f"PS5-=https://www.newegg.com/p/N82E16868110292&t={t}",
        # f"XBOXSERIESX-=https://www.bestbuy.com/site/xbox-series-x-and-s/xbox-series-x-and-s-consoles/pcmcat1586900952752.c?id=pcmcat1586900952752",
        # f"XBOXSERIESX-=https://www.newegg.com/p/N82E16868105273&t={t}"
    }
    s = AsyncHTMLSession()

    tasks = (parse_url(s, url.split("-=")[1], url.split("-=")[0]) for url in urls)

    return await asyncio.gather(*tasks)


# Determine whether or not to parse Best Buy or NewEgg.
async def parse_url(s, url, model):
    if "bestbuy" in url:
        await parse_bestbuy_url(s, url, model)
    if "newegg" in url:
        await parse_newegg_url(s, url, model)
    if "bhphotovideo" in url:
        await parse_bh_url(s, url, model)
    if "amd" in url:
        await parse_amd_url(s, url, model)


async def parse_bestbuy_url(s, url, model):
    headers = {
        "Authority": "www.bestbuy.com",
        "Method": "GET",
        "Path": url.split("https://www.bestbuy.com")[1],
        "Scheme": "https",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Cookie": '',
        "Pragma": "no-cache",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": Util.get_random_user_agent(),
        "Referer": "https://www.google.com/"
    }
    # Narrow HTML search down using HTML class selectors.
    r = await s.get(url, headers=headers)
    items = r.html.find('.right-column')

    for item in items:
        item = Item.create_from_bestbuy(item, model)

        if item is not None:
            item_id = item.get_item_id()
            if item_id in item_set.keys():
                if item_set[item_id].get_button_text() != item.get_button_text():
                    original_text = item_set[item_id].get_button_text()
                    if item.is_in_stock():
                        notify_difference(item, original_text)

            item_set[item_id] = item


async def parse_newegg_url(s, url, model):
    headers = {
        "Authority": "www.newegg.com",
        "Method": "GET",
        "Path": url.split("https://www.newegg.com")[1],
        "Scheme": "https",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Cookie": '',
        "Pragma": "no-cache",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": Util.get_random_user_agent(),
        "Referer": "https://www.google.com/"
    }
    r = await s.get(url, headers=headers)
    items = r.html.find('.item-cell')

    for item in items:
        item = Item.create_from_newegg(item, model)

        if item is not None:
            item_id = item.get_item_id()
            if item_id in item_set.keys():
                if item_set[item_id].get_button_text() != item.get_button_text():
                    original_text = item_set[item_id].get_button_text()
                    if item.is_in_stock():
                        notify_difference(item, original_text)

            item_set[item_id] = item

async def parse_amd_url(s, url, model):
    headers = {
        "Authority": "www.amd.com",
        "Method": "GET",
        "Path": "/en/direct-buy/us",
        "Scheme": "https",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        # "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Cookie": '',
        "Pragma": "no-cache",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": Util.get_random_user_agent(),
        "Referer": "https://www.google.com/"
    }

    r = await s.get(url, headers=headers)
    items = r.html.find('[class="btn-radeon"]')
    isSoldOut = items[0].text == "SOLD OUT"
    if(not isSoldOut):
        print("https://www.amd.com/en/direct-buy/us")
        webbrowser.open_new("https://www.amd.com/en/direct-buy/us")


async def parse_bh_url(s, url, model):
    headers = {
        "Authority": "www.bhphotovideo.com",
        "Method": "GET",
        "Path": url.split("https://www.bhphotovideo.com")[1],
        "Scheme": "https",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        #"Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Cookie": '',
        "Pragma": "no-cache",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": Util.get_random_user_agent(),
        "Referer": "https://www.google.com/"
    }
    r = await s.get(url, headers=headers)
    items = r.html.find('[data-selenium="miniProductPageProduct"]')

    for item in items:
        item = Item.create_from_bh(item, model)

        if item is not None:
            item_id = item.get_item_id()
            if item_id in item_set.keys():
                if item_set[item_id].get_button_text() != item.get_button_text():
                    original_text = item_set[item_id].get_button_text()
                    if item.is_in_stock():
                        notify_difference(item, original_text)

            item_set[item_id] = item


if __name__ == '__main__':
    print(f"{time.ctime()} ::: Checking Stock...")
    Util.clear_shelf("items")
    while True:
        item_set = Util.get_dict("items")
        try:
            asyncio.run(get_stock())
        except Exception as e:
            if "SSLError" in type(e).__name__:
                # SSL Error. Wait 7-10 seconds and try again.
                print(f"{time.ctime()} ::: {type(e).__name__} error. Retrying in 7-10 seconds...")
            else:
                print(f"{type(e).__name__} Exception: {str(e)}")

        Util.set_shelf("items", item_set)
        time.sleep(random.randint(7, 10))


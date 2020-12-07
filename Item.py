class Item:
    def __init__(self, model, price, item_number, name, url, btn_text):
        self.name = name
        self.model = model
        self.price = price
        self.item_number = item_number
        self.url = url
        self.btn_text = btn_text

    def get_name(self):
        return self.name

    def get_url(self):
        return self.url

    def get_button_text(self):
        return self.btn_text

    def get_model(self):
        return self.model

    def get_item_id(self):
        return self.item_number

    def get_price(self):
        return self.price

    def is_in_stock(self):
        return "cart" in self.btn_text.lower()

    def get_founders_price(self):
        founders_price = {
            "3070": 500,
            "3080": 700,
            "3090": 1500,
            "6800": 580,
            "6800 XT": 650,
            "6900 XT": 999,
            "Ryzen 9 5950X": 800,
            "Ryzen 9 5900X": 550,
            "Ryzen 7 5800X": 450,
            "Ryzen 5 5600X": 300
        }

        return founders_price[self.model]

    def is_way_overpriced(self, price):
        price_as_float = float(''.join(d for d in price if d.isdigit() or d == '.'))
        return abs(price_as_float - self.get_founders_price()) > 300


    def create_from_bestbuy(html, model):
        header = html.find('.sku-header', first=True)
        price_parent = html.find('.priceView-customer-price', first=True)
        price = price_parent.find('span', first=True).text

        stock_button = html.find('.sku-list-item-button', first=True).find('.btn', first=True)
        header_text = header.text.replace("New!","")
        if "Ryzen" in model:
            model = header_text.split("AMD - ")[1].split(" 4th")[0]
        item_url = f"https://www.bestbuy.com{header.find('a', first=True).attrs['href']}"
        item_id = item_url.split("skuId=")[1]

        new_item = Item(model, price, item_id, header_text, item_url, stock_button.text)

        # Check price. Make sure it's within at least $300 of the FE price.
        if new_item.is_way_overpriced(price):
            return None

        return new_item

    def create_from_newegg(html, model):
        header = html.find('.item-info', first=True)
        name = html.find('.item-title', first=True)
        if "Ryzen" in model:
            model = f'{name.text.split("AMD ")[1].split("0X ")[0]}0X'
        price_parent = html.find('.price-current', first=True)

        # NewEgg sometimes displays "sold out" instead of a price. This will
        # get a price if it's shown.
        try:
            price = f"{price_parent.text.split('.')[0]}.{price_parent.text.split('.')[1][0:2]}"
        except:
            # If the price can't be gathered, just set it to 'unknown' for now.
            price = "Unknown"

        stock_button = html.find('.item-button-area', first=True).find('.btn', first=True)
        item_url = html.find('.item-container', first=True).find('a', first=True).attrs['href']

        item_features = html.find('.item-features', first=True).find('li')
        for feature in item_features:
            if "item #" in feature.text.lower():
                item_id = feature.text.split(": ")[1]
                break

        if "item_id" not in locals():
            return None

        new_item = Item(model, price, item_id, name.text, item_url, stock_button.text)

        # Check price. Make sure it's within at least $300 of the FE price.
        if "Unknown" not in price:
            if new_item.is_way_overpriced(price):
                return None

        return new_item

    def create_from_bh(html, model):
        product = html.find('[data-selenium="miniProductPageName"] > a', first=True)
        item_name = product.text
        item_url = f"https://www.bhphotovideo.com{product.attrs['href']}"

        item = html.find('[data-selenium="miniProductPageProductSkuInfo"]', first=True)
        item_id = item.text.split("# ")[1].split(" ")[0]

        price_container = html.find('[data-selenium="miniProductPagePricingCurrency"]', first=True)
        price_string = f"{price_container.text[:-2]}.{price_container.text[-2:]}"

        stock_button = html.find('[data-selenium="addToCartButton"]', first=True)

        if stock_button is None:
            stock_button_text = "Out of Stock"
        else:
            stock_button_text = "Add to Cart"

        new_item = Item(model, price_string, item_id, item_name, item_url, stock_button_text)

        # Check price. Make sure it's within at least $300 of the FE price.
        if new_item.is_way_overpriced(price_string):
            return None

        return new_item

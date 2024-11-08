from scrapy import Item, Field

class AmazonProductItem(Item):
    rank = Field()
    asin = Field()
    title = Field()
    price = Field()
    link = Field()
    rating = Field()
    reviews = Field()
    bought_last_month = Field()
    type = Field()
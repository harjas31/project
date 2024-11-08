class AmazonScraperPipeline:
    def process_item(self, item, spider):
        # Clean up price
        if item['price'] != 'N/A':
            item['price'] = item['price'].replace(',', '').strip()
            
        # Clean up reviews count
        if item['reviews'] != 'N/A':
            item['reviews'] = item['reviews'].replace(',', '').strip()
            
        return item
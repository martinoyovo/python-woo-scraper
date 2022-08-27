import requests
from bs4 import BeautifulSoup
import random
import pandas as pd


PRODUCT_URL = f'https://www.fabellashop.com/categorie-produit/maquillageongles/teint/'


BASE_URL = 'http://www.floatrates.com'

CURRENCY_URL = f'{BASE_URL}/feeds.html'

CONVERSION_PATH = f'{BASE_URL}/daily'
XOF_URL = f'{CONVERSION_PATH}/xof.xml'


class WooCommerceScraper(object):
    @classmethod
    def httpFetcher(self, URL):
        with requests.Session() as session:
            result = session.get(URL)
            result = result.text
            return result
        
    @classmethod
    def scrapLink(self, URL, format='html.parser'):
        result = self.httpFetcher(URL)
        return BeautifulSoup(
            result, format)
    
    @classmethod
    def getProducts(self, URL):
        
        soup = self.scrapLink(URL)        
                
        products = soup.find_all('h2', class_='woocommerce-loop-product__title')
        if not products:
            products = soup.find_all('p', class_='product-title')
            
        prices = soup.find_all('span', class_='woocommerce-Price-amount')
        
        finalProducts = []
        for (item,price_with_curreny) in zip(products, prices):
            title = item.text
            
            price_with_curreny = price_with_curreny.text.split('\xa0')
            
            price = float(price_with_curreny[0])
            currency = price_with_curreny[-1]
        
            
            finalProducts.append({
                "title": title,
                "price": price,
                "quantity": 1,
                "currency": currency
            })
            
        return finalProducts
        
    @classmethod
    def getXOFConversions(self, URL):
            
        soup = self.scrapLink(URL)
        
        soup = soup.find_all("item")
        
        soup = random.sample(soup, 6)
        
        conversions = []
        for item in soup:
            item = item.find('title').text.split(" ")
            conversions.append({"currency": item[-1], "value": float(item[3])})    
        return conversions
    
    @classmethod
    def getCurrencies(self, URL):
        new_devise = []

        soup = self.scrapLink(URL, format="lxml") 
        
        soup = soup.find(attrs={"id": "pb_1426"})
        soup = soup.find_all("ul")
                
        for s in soup:
            scrapped_currencies = s.find_all('li')

            factory = [
                item.find_all('a')
                for item in scrapped_currencies
            ]
            
            factory = [
                x[0].string.strip()
                for x in factory
            ]
            
            for x in factory:
                x = x.split('(')
                x = x[-1].split(')')
                x = x[0]
                new_devise.append(x)
            
        return new_devise
            
    @classmethod
    def convertFromXOF(self, products):
        new_currencies = self.getXOFConversions(XOF_URL)
        
        for new_currency in new_currencies:
            for item in products:
                item.update({new_currency["currency"]: item["price"] * new_currency["value"]})
                
        return products
    
    @classmethod
    def saveToFile(self, products):
        df = pd.DataFrame(products)
        
        df.to_csv('products_list.csv', index=False)
        
    @classmethod
    def readDataFromFile(self):
        df = pd.read_csv('products_list.csv')

        return df  
    
    @classmethod
    def main(cls):
        productsTitle = WooCommerceScraper.getProducts(PRODUCT_URL)
        
        products = WooCommerceScraper.convertFromXOF(productsTitle)
        WooCommerceScraper.saveToFile(products)
        
        data = WooCommerceScraper.readDataFromFile()
        return data
        

data = WooCommerceScraper.main()
print(data)
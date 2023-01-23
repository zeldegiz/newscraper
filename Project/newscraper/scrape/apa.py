import urllib3
from bs4 import BeautifulSoup
from datetime import datetime

class scraper():
    def __init__(self, last_link=None):
        self.month = (0,'yanvar','fevral', 'mart', 'aprel', 'may', 'iyun', 'iyul', 'avqust', 'sentyabr', 'oktyabr', 'noyabr', 'dekabr')
        self.last_link = last_link
        self.http = urllib3.PoolManager()
        
    def get_news_links(self):
        index = self.http.request('GET', 'https://apa.az/az', headers = {'User-agent': 'Mozilla/5.0'}).data.decode('utf-8')
        
        parser = BeautifulSoup(index, 'lxml')
        a_items = parser.find('div', {'class':'news'}).find_all('a', {'class':'item'})

        urls = [link['href'] for link in a_items]
        if(self.last_link):
            try:
                urls = urls[:urls.index(self.last_link)]
            except:
                pass
        return urls
        
    def data_extractor(self, responses):
        extracted_data = []
        error_urls = []
        for url, text in responses.items():
            try:
                content = BeautifulSoup(text, 'lxml')
                data = {'url': url}
                data['header'] = content.find('h2', {'class':'title_news mb-site'}).text
                data['image'] = content.find('div', {'class':'main_img'}).find('img')['src']
                d = content.find('div', {'class':'date'}).find('span').text
                day, month, year, time = d.split(' ')[:-2]
                data['datetime'] = datetime(int(year), int(self.month.index(month))+1, int(day), int(time.split(':')[0]), int(time.split(':')[1]))
                data['news_content'] = content.find('div', {'class':'texts mb-site'}).get_text()
                data['category'] = content.find('div', {'class':'breadcrumb_row'}).find('h1').get_text()
                data['author'] = content.find('div', {'class':'tags mt-site'}).find('span').text
                tags = content.find('div', {'class':'tags mt-site'}).find('div',{'class':'links'}).find_all('a')
                data['tags'] = [tag.text.lower() for tag in tags]
            
                extracted_data.append(data)
            except:
                error_urls.append(url)
                
        return extracted_data, error_urls
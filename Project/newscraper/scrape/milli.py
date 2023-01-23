import urllib3
from bs4 import BeautifulSoup
from datetime import datetime

class scraper():
    def __init__(self, last_link=None):
        self.month = (0,'yanvar','fevral', 'mart', 'aprel', 'may', 'iyun', 'iyul', 'avqust', 'sentyabr', 'oktyabr', 'noyabr', 'dekabr')
        self.last_link = last_link
        self.http = urllib3.PoolManager()
        
    def get_news_links(self):
        urls = []
        ts = '0'
        _break = False
        
        for i in range(20):
            index = self.http.request('GET', f'https://news.milli.az/latest.php?isAjax=1&ts={ts}', headers = {'User-agent': 'Mozilla/5.0'}).data.decode('utf-8')
            parser = BeautifulSoup(index, 'lxml')
            
            for div in parser.find('ul',{'class':'post-list2'}).find_all('div', {'class':'text-holder'}):
                url = div.find('a')['href']
                if(url == self.last_link):
                    _break = True
                    break
                urls.append(url)
            if(_break):
                break
            ts = parser.find('script').text.strip()[:-1].split('=')[1].strip().split(',')[1].split(':')[1][2:-2]
        
        return urls
        
    def data_extractor(self, responses):
        extracted_data = []
        error_urls = []
        for url, text in responses.items():
            try:
                content = BeautifulSoup(text, 'lxml').find('div', {'class': 'quiz-holder'})
            
                data = {'url': url}
                data['header'] = content.find('h1').text
                data['image'] = content.find('img', {'class':'content-img'})['src']
                d = content.find('div', {'class':'date-info'}).text
                day, month, year, time = d.split(' ')
                month = month.lower()
                data['datetime'] = datetime(int(year), int(self.month.index(month))+1, int(day), int(time.split(':')[0]), int(time.split(':')[1]))
                data['news_content'] = content.find('div', {'class':'article_text'}).get_text()
                data['category'] = content.find('span', {'class':'category'}).text
                data['author'] = content.find('div', {'class':'article_text'}).find('strong').text
                tags = content.find('div', {'class':'tags_list'}).find_all('a')
                data['tags'] = [tag.text.lower()[1:] for tag in tags]
                extracted_data.append(data)
            except:
                error_urls.append(url)
        return extracted_data, error_urls
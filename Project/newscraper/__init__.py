from . import scrape
from . import database
import json
import urllib3
import concurrent.futures
from urllib.parse import urlparse

def url_validator(url, website):
    try:
        result = urlparse(url)
        if(result.netloc.lower() not in website):
            return False
        return all([result.scheme, result.netloc])
    except:
        return False
        
def fetch(url, cmanager):
    response = cmanager.request('GET', url, headers = {'User-agent': 'Mozilla/5.0'})
    if(response and response.status == 200):
        return (url,response.data.decode('utf-8'))
    return (url, None)

def start():
    with open('config.json') as file:
        config = json.loads(file.read())
    
    
    apa = scrape.apa(config['last_urls']['apa.az'])
    milli = scrape.milli(config['last_urls']['milli.az'])
    
    apa_links = apa.get_news_links()
    milli_links = milli.get_news_links()
    
    apa_links_filtered = filter(lambda url: url_validator(url,['apa.az','www.apa.az']),apa_links)
    milli_links_filtered = filter(lambda url: url_validator(url, ['news.milli.az','www.news.milli.az']), milli_links)
    
    manager = urllib3.PoolManager(maxsize=20)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        results_futures = list(map(lambda url: executor.submit(fetch, url, manager), apa_links_filtered))
        apa_results = [f.result() for f in concurrent.futures.as_completed(results_futures)]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        results_futures = list(map(lambda url: executor.submit(fetch, url, manager), milli_links_filtered))
        milli_results = [f.result() for f in concurrent.futures.as_completed(results_futures)]
    
    
    apa_datas = {url:text for url,text in apa_results}
    apa_datas, apa_error_links = apa.data_extractor(apa_datas)
    
    milli_datas = {url:text for url,text in milli_results}
    milli_datas, milli_error_links = milli.data_extractor(milli_datas)
    db_params = config['database']
    db = database.database(db_params['url'],db_params['user'],db_params['pass'], db_params['port'])
    db.create_tables()
    for data in milli_datas+apa_datas:
        db.insert(**data)
        
    if(len(apa_links)>0):
        config['last_urls']['apa.az'] = apa_links[0]
    if(len(milli_links)>0):
        config['last_urls']['milli.az'] = milli_links[0]
    
    with open('config.json', 'wt') as file:
        file.write(json.dumps(config))
    
    
    
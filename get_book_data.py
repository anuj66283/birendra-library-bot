from bs4 import BeautifulSoup as bs
from cachetools import cached, TTLCache
import requests

hdr = {
    'Accept': 'text/html, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.8',
    'Host': 'birendra.elibrary.edu.np',
    'Origin': 'http://birendra.elibrary.edu.np',
    'Referer': 'http://birendra.elibrary.edu.np/',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0.1; ALE-L23) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36'
}

uri = 'http://birendra.elibrary.edu.np/Catalouge/BookStatus?bookId='

@cached(cache=TTLCache(maxsize=1024, ttl=600))
def get_html(id):
    a = requests.post(uri+id).text
    return a

def main(id):
    htm = get_html(id)
    soup = bs(htm, 'lxml').table
    all_tr = soup.tbody.find_all('tr')

    rslt = {'BookID': id}

    for x in all_tr:
        k = x.td.text.split(':')
        val = x.td.find_next_sibling().text
        rslt[k[0]] = val
    rslt[soup.tfoot.tr.th.text.split(':')[0]] = soup.tfoot.tr.td.text

    return rslt
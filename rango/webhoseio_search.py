import webhoseio
from keys import WEBHOSEIO_API_KEY

def run_query(search_term):
    webhoseio.config(token=WEBHOSEIO_API_KEY)
    query_params = {
        "q": "\"{}\" language:english".format(search_term),
        "sort": "crawled"
    }
    output = webhoseio.query("filterWebContent", query_params)
    results = []
    for result in output['posts'][:10]:
        title = result['thread']['title']
        url = result['thread']['url']
        site = result['thread']['site']
        site_full = result['thread']['site_full']
        print site_full
        results.append({'title': title, 'url': url, 'site': site, 'site_full': site_full})

    return results

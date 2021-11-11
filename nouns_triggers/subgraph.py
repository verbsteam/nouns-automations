import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry


def query_subgraph(query: str) -> dict:
    """
    Queries the nounsdao subgraph on thegraph.com
    Uses a http adapter with retries because thegraph sometimes is not available.

    Parameters
    ----------
    query : graphql query string

    Returns
    -------
    dict object of the response
    """
    s = get_requests_session()
    subgraph_endpoint = "https://api.thegraph.com/subgraphs/name/nounsdao/nouns-subgraph"
    response = s.post(subgraph_endpoint, json={"query": query})
    response.raise_for_status()
    subgraph_response = response.json()['data']
    return subgraph_response


def get_requests_session():
    s = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504], allowed_methods=['GET', 'POST'])
    adapter = HTTPAdapter(max_retries=retries)
    s.mount('https://', adapter)
    return s

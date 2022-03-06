import httpx
from bs4 import BeautifulSoup


def int_k(string_k: str):
    """
        Convert strings ending with 'k's to an integer
    Arguments:
        string_k: string

    Returns:
        number_k : string
    """
    number_k = float(string_k.replace("k", "").replace("K", ""))
    number_k = int(number_k * 1000)
    return number_k


def get_redirect_url(query_url: str):
    """
    Returns the last URL in history of redirects
    API:
        https://github.com/encode/httpx/httpx/_models.py

    Arguments:
        query: string

    Returns:
         [redirected_url, response_site]: list


    """
    response = httpx.get(
        query_url,
        timeout=10,
        follow_redirects=True,
    )
    response_site = response.url.host

    # Get History of redirect URLS
    history_urls = []
    for history in response.history:
        history_url = history.url.__str__()
        history_urls.append(history_url)

    history_urls.append(response.url)

    # Discard login redirect URLs of facebook, instagram and etc.,
    if "login" in str(history_urls[-1:][0]) or "authwall" in str(history_urls[-1:][0]):
        redirected_url = str(history_urls[-2:][0])
    else:
        redirected_url = str(history_urls[-1:][0])

    return [redirected_url, response_site]


def string_to_number(number_string: str) -> int:
    try:
        if number_string is not None:
            int_number = int(number_string.replace(",", ""))
        else:
            int_number = 0
    except ValueError:
        int_number = 0
    return int_number

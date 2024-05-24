from llama_index.readers.web import TrafilaturaWebReader,AsyncWebPageReader,BeautifulSoupWebReader,SimpleWebPageReader
import requests
from bs4 import BeautifulSoup
from typing import Union,List
from enum import Enum
class WebProvider(Enum):
    TRAFILATURA = 0
    ASYNCWEBPAGE = 1
    WEBPAGE = 2
    BEAUTIFULSOUP = 3

class CustomWebLoader():
    def __init__(self,web_provider : WebProvider = WebProvider.TRAFILATURA):
        # Define web provider
        self._web_provider = web_provider

        # Specify web provider
        self._web_loader = None
        if self._web_provider == WebProvider.TRAFILATURA:
            # Trafilatura
            self._web_loader = TrafilaturaWebReader()
        elif self._web_provider == WebProvider.WEBPAGE:
            # Base Web Loader
            self._web_loader = SimpleWebPageReader()
        elif self._web_provider == WebProvider.ASYNCWEBPAGE:
            # Async Web Loader
            self._web_loader = AsyncWebPageReader()
        elif self._web_provider == WebProvider.BEAUTIFULSOUP:
            # Async Web Loader
            self._web_loader = BeautifulSoupWebReader()
        else:
            raise Exception(f"Service {self._web_provider} is not supported!")

    def load_data(self,url: Union[List[str],str]):
        # Convert string to list of string
        if isinstance(url,str): url = [url]
        return self._web_loader.load_data(url)

    async def aload_data(self,url: Union[List[str],str]):
        # Convert string to list of string
        if isinstance(url, str): url = [url]
        # Return data
        result = await self._web_loader.aload_data(url)
        return result


class WebUtils():
    @staticmethod
    def get_sub_link(root_url):
        reqs = requests.get(root_url)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        external_urls = []
        sub_urls = []

        for link in soup.find_all('a'):
            # Remove space
            url_link = str(link.get('href'))
            # Strip
            url_link = url_link.strip()

            # Sub link case
            if url_link.startswith("/"):
                sub_urls.append(root_url+url_link)
            elif url_link.startswith("http"):
                external_urls.append(url_link)
            else:
                pass
                # print(url_link)
        # Unique url
        sub_urls = list(set(sub_urls))
        external_urls = list(set(external_urls))
        return sub_urls,external_urls






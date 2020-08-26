from stores.store import Store
from models.category import Category
from models.book import Book

import os
import json
import slug
import requests
from concurrent.futures import ProcessPoolExecutor, as_completed

def download_file(url: str, outdir: str, req_config: dict, overwritten: bool = False) -> str:
    if not isinstance(url, str):
        return ''
    
    if len(url) <= 0:
        return ''
    
    full_path = url.replace('/', os.sep)
    dir_name, file_name = os.path.split(full_path)
    file_path: str = os.path.join(outdir, file_name)

    if os.path.exists(file_path) and (os.path.getsize(file_path) > 0) and not overwritten:
        return file_path

    verify: bool = req_config.get('verify', True)
    proxies: dict = req_config.get('proxies', None)
    timeout: int = req_config.get('timeout', None)
    response: requests.Response = None
    try:
        response = requests.get(url, stream=True, verify=verify, proxies=proxies, timeout=timeout)
    except Exception as ex:
        print(f'{__file__}[31]: Exception: {ex}')
        return ''
    
    if response.status_code != 200:
        print(f'{__file__}[35]: response.status_code={response.status_code}')
        return ''
    
    try:
        with open(file_path, 'wb') as downloading_file:
            downloading_file.write(response.content)
    except Exception as ex:
        print(f'{__file__}[46]: Exception: {ex}')
        response.close
        return ''
    
    response.close()
    return file_path

def download_book(book: Book, config: dict, outdir: str) -> bool:
    if not isinstance(book, Book):
        return False
    
    if not isinstance(book.links, dict) or len(book.links) <= 0:
        return False

    download_config: dict = config.get('download', {})
    requests_config: dict = config.get('requests', {})
    output_dir: str = outdir
    if not isinstance(outdir, str):
        output_dir = '.'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    result: bool = False

    if len(book.image) > 0 and download_config.get('image', True):
        book.image = download_file(book.image, output_dir, requests_config, download_config.get('overwritten', False))
        result = True

    if isinstance(book.links, dict) and len(book.links) > 0 and download_config.get('media', True):
        link: str = ''
        for format in book.links.keys():
            link = book.links[format]
            if len(link) > 0:
                book.links[format] = download_file(link, output_dir, requests_config, download_config.get('overwritten', False))
                result = True
    
    #try:
        #with open(f'{slug.slug(book.title)}.json', 'w') as json_file:
            #json.dump(book.to_json(), json_file, indent=4, sort_keys=True)
    #except Exception as ex:
        #pass
    
    return result


class Downloader(object):
    @property
    def store(self) -> Store:
        return self._store

    @property
    def config(self) -> dict:
        return self._config

    @property
    def categories(self) -> list:
        return self._categories
    
    def __init__(self, store: Store, config: dict = None, categories: list = None, keyword: str = None, outdir: str = None):
        self._store = store
        self._config = config
        self._categories = None
        if keyword is None:
            self._filtered_categories = categories
            self._search_keyword = None
        else:
            self._search_keyword = keyword
            self._filtered_categories = None
        if not isinstance(outdir, str):
            self._outdir = '.'
        else:
            self._outdir = outdir

    def _internal_init(self) -> bool:
        return True

    def _parse_categories(self) -> list:
        return []

    def _count_pages(self, cat: Category) -> int:
        return 0

    def _parse_books(self, cat: Category, page: int = 1) -> list:
        return []

    def _browse_book(self, book: Book) -> bool:
        return False

    def init(self) -> bool:
        return self._internal_init()

    def __string_in_list(self, string: str, string_list: list) -> bool:
        if not isinstance(string, str) or not isinstance(string_list, list):
            return False
        for current_str in string_list:
            if current_str.lower() == string.lower():
                return True
        return False

    def download(self) -> list:
        if self._categories is None or len(self._categories) <= 0:
            self._categories = self._parse_categories()
        
        books: list = []
        cat: Category = None
        for cat in self._categories:
            if self._filtered_categories is None or len(self._filtered_categories) <= 0 or (self.__string_in_list(cat.description, self._filtered_categories)):
                print(f'Category: {cat.description}')
                if cat.pages == 0:
                    cat.pages = self._count_pages(cat)
                for page in range(1, cat.pages+1):
                    print(f'  -> Page: {page}/{cat.pages}')
                    parsed_books: list = self._parse_books(cat, page)
                    for book in parsed_books:
                        if self._browse_book(book):
                            print(f'\t\tBook: {book.title}')
                    with ProcessPoolExecutor(max_workers=32) as executor:
                        features_to_books = {executor.submit(download_book, book, self._config, self._outdir) : book for book in parsed_books}
                        for feature in as_completed(features_to_books):
                            if feature.result():
                                book: Book = features_to_books[feature]
                                if isinstance(book, Book):
                                    books.append(book)
        return books
from stores.store import Store
from models.category import Category
from models.book import Book

import os
from concurrent.futures import ProcessPoolExecutor, as_completed

def download_book(book: Book, config: dict) -> bool:
    if not isinstance(book, Book):
        return False
    
    if not isinstance(book.media, dict) or len(book.media) <= 0:
        return False

    download_config: dict = config.get('download')
    output_dir: str = download_config.get('directory', '')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for format in book.media.keys():
        link: str = book.media[format]
        link = link.replace('/', os.sep)
        path, name = os.path.split(link)
        book.path = os.path.join(output_dir, name)
    
    print(book)
    
    return True


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
    
    def __init__(self, store: Store, config: dict = None, categories: list = None):
        self._store = store
        self._config = config
        self._categories = None
        self._filtered_categories = categories

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

    def download(self) -> list:
        if self._categories is None or len(self._categories) <= 0:
            self._categories = self._parse_categories()
        
        books: list = []
        cat: Category = None
        for cat in self._categories:
            if self._filtered_categories is None or len(self._filtered_categories) <= 0 or cat.description in self._filtered_categories:
                if cat.pages == 0:
                    cat.pages = self._count_pages(cat)
                for page in range(1, cat.pages+1):
                    parsed_books: list = self._parse_books(cat, page)
                    for book in parsed_books:
                        self._browse_book(book)
                        books.append(book)
                    with ProcessPoolExecutor(max_workers=16) as executor:
                        feature_of_books = {executor.submit(download_book, b, self._config) : b for b in parsed_books}
                        for feature in as_completed(feature_of_books):
                            book = feature_of_books[feature]
        return books
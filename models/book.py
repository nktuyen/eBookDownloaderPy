class Book(object):
    @property
    def url(self) -> str:
        if not isinstance(self._url, str):
            return ''
        return self._url

    @property
    def title(self) -> str:
        if not isinstance(self._title, str):
            return ''
        return self._title

    @title.setter
    def title(self, val: str):
        self._title = val

    @property
    def image(self) -> str:
        if not isinstance(self._image, str):
            return ''
        return self._image
    
    @image.setter
    def image(self, val: str):
        self._image = val

    @property
    def media(self) -> dict:
        if not isinstance(self._media, dict):
            return None
        return self._media

    @media.setter
    def media(self, val: dict):
        self._media = val

    @property
    def isbn(self) -> str:
        if not isinstance(self._isbn10, str):
            return ''
        return self._isbn10
    
    @isbn.setter
    def isbn(self, val: str):
        self._isbn10 = val
    
    @property
    def brief(self) -> str:
        if not isinstance(self._brief, str):
            return ''
        return self._brief

    @brief.setter
    def brief(self, val: str):
        self._brief = val

    @property
    def authors(self) -> list:
        return self._authors
    
    @authors.setter
    def authors(self, val: list):
        self._authors = val

    @property
    def publisher(self) -> str:
        if not isinstance(self._publisher, str):
            return ''
        return self._publisher
    
    @publisher.setter
    def publisher(self, val: str):
        self._publisher = val

    @property
    def published(self) -> int:
        if not isinstance(self._published_year, int):
            return 0
        return self._published_year

    @published.setter
    def published(self, val: int):
        self._published_year = val

    @property
    def pages(self) -> int:
        if not isinstance(self._pages, int):
            return 0
        return self._pages

    @pages.setter
    def pages(self, val: int):
        self._pages = val

    @property
    def categories(self) -> list:
        return self._categories
    
    @categories.setter
    def categories(self, val: list):
        self._categories = val

    @property
    def path(self) -> str:
        if not isinstance(self._path, str):
            return ''
        return self._path

    @path.setter
    def path(self, val: str):
        self._path = val

    def __init__(self, url: str, title: str = ''):
        self._url = url
        self._title = title
        self._isbn10 = ''
        self._brief = ''
        self._image = ''
        self._media = ''
        self._authors = None
        self._publisher = None
        self._published_year = 0
        self._pages = 0
        self._categories = None
        self._path = ''
    
    def __str__(self):
        return f'{{"isbn-10": "{self._isbn10}", "title": "{self._title}", "url": "{self._url}", "pages": {self._pages}, "published": {self._published_year}, "media": {self._media}, "path":"{self._path}"}}'
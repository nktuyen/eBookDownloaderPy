class Category(object):
    @property
    def name(self) -> str:
        if self._name is None:
            return ''
        return self._name

    @property
    def url(self) -> str:
        if self._url is None:
            return ''
        return self._url

    @property
    def description(self) -> str:
        if self._desc is None:
            return ''
        return self._desc

    @property
    def pages(self) -> int:
        return self._pages

    @pages.setter
    def pages(self, val: int):
        self._pages = val
        return self
    
    def __init__(self, name: str, url: str, description: str = None):
        self._name = name
        self._url = url
        self._desc = description
        self._pages = 0
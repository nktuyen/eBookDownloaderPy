class Store:
    @property
    def name(self) -> str:
        if self._name is None:
            return ''
        return self._name

    @property
    def home(self) -> str:
        if self._home is None:
            return ''
        return self._home

    @property
    def description(self) -> str:
        if self._desc is None:
            return ''
        return self._desc

    def __init__(self, home: str, name: str, desc: str = None):
        self._home = home
        self._name = name
        self._desc = desc
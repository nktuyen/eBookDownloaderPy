from stores.store import Store

class AllITeBooksStore(Store):
    def __init__(self):
        super().__init__(name='allitebooks', home='http://www.allitebooks.org', desc='All IT eBooks - Free IT eBooks Download')
from stores.allitebooks import AllITeBooksStore
from downloaders.allitebooks import AllITeBooksDownloader
from downloaders.downloader import Downloader

import sys
import os
import json
import optparse

if __name__ == "__main__":
    parser = optparse.OptionParser('%prog store [options]')
    parser.add_option('--config', default=None, help='Configuration file in JSON format')
    parser.add_option('--categories', default=None, help='Categories list seperated by comma')
    options, arguments = parser.parse_args()

    if arguments is None or len(arguments) <= 0:
        parser.print_usage()
        sys.exit(1)

    stores_d: dict = dict()
    stores_l: list = list()
    
    store = AllITeBooksStore()
    stores_d[store.name] = store
    stores_l.append(store)
    
    specified_stores: list = []

    for arg in arguments:
        if arg.isnumeric():
            idx: int = int(arg)
            if idx <= 0 or idx > len(stores_l):
                print(f'Specified store index is out of range:{idx}')
                sys.exit(2)
            specified_stores.append(stores_l[idx-1])
        else:
            name: str = arg
            if name not in stores_d:
                print(f'Store with specified name is not exist:{name}')
                sys.exit(2)
            specified_stores.append(stores_d[name])

    if len(specified_stores) <= 0:
        specified_stores = stores_d.values()
    
    config: dict = None
    categories: list = None

    if options.config is None:
        config = dict()
    else:
        if not os.path.exists(options.config):
            print(f'Specified configuration file is not exist:{options.config}')
            sys.exit(3)
        try:
            with open(options.config, 'r', encoding='utf-8') as json_file:
                config = json.load(json_file)
        except Exception as ex:
            print(f'An error ocurr during reading configuration file:{ex}')
            sys.exit(4)
    
    if options.categories is not None:
        categories = []
        cat_s: str = str(options.categories).strip()
        arr = cat_s.split(',')
        for cat in arr:
            if len(cat.strip()) > 0:
                categories.append(cat.strip())

    downloader: Downloader = None
    books: list = []
    for store in specified_stores:
        if isinstance(store, AllITeBooksStore):
            downloader = AllITeBooksDownloader(store, config, categories)
        else:
            continue
        books += downloader.download()
    
    with open('books.json', 'w') as json_file:
        json.dump(books, json_file, indent=4)
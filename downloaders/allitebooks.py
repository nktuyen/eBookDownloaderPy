from downloaders.downloader import Downloader
from stores.allitebooks import AllITeBooksStore
from models.category import Category
from models.book import Book
from AdvancedHTMLParser import AdvancedHTMLParser, MultipleRootNodeException, AdvancedTag
from urllib.parse import quote, unquote
from html2text import html2text
from html import escape, unescape
import requests
from concurrent.futures import ProcessPoolExecutor, as_completed


class AllITeBooksDownloader(Downloader):
    def __init__(self, store: AllITeBooksStore, config: dict = None, categories: list = None):
        super().__init__(store=store, config=config, categories=categories)

    def _parse_categories(self):
        return [
            Category('web-development', 'http://www.allitebooks.org/web-development/', 'Web Development'),
            Category('programming', 'http://www.allitebooks.org/programming/', 'Programming'),
            Category('datebases', 'http://www.allitebooks.org/datebases/', 'Datebases'),
            Category('networking-cloud-computing', 'http://www.allitebooks.org/networking-cloud-computing/', 'Networking & Cloud Computing'),
            Category('administration', 'http://www.allitebooks.org/administration/', 'Administration'),
            Category('computers-technology', 'http://www.allitebooks.org/computers-technology/', 'Computers & Technology'),
            Category('software', 'http://www.allitebooks.org/software/', 'Software')
        ]

    def _count_pages(self, cat: Category) -> int:
        if not isinstance(cat, Category):
            return 0
        response: requests.Response = None
        url: str = cat.url
        req_config: dict = None
        if isinstance(self._config, dict):
            req_config = self._config.get('requests', {})
        verify: bool = req_config.get('verify', True)
        proxies: dict = req_config.get('proxies', None)
        
        try:
            response = requests.get(url, proxies=proxies, verify=verify, timeout=3)
        except Exception as ex:
            print(f'Exception: {ex}')
            return 0
        
        if response.status_code != 200:
            print(f'response.status_code: {response.status_code}')
            return 0
        
        parser: AdvancedHTMLParser = AdvancedHTMLParser()
        try:
            parser.parseStr(response.text)
        except MultipleRootNodeException:
            pass
        except Exception as ex:
            print(f'Exception: {ex}')
            response.close()
            return  0
        
        response.close()
        body: AdvancedTag = parser.body
        if not isinstance(body, AdvancedTag):
            print(f'Body is not AdvancedTag')
            parser.close()
            return 0
        
        pages: int = 1

        tag_list: list = None
        try:
            tag_list = body.getElementsByXPath("//main[@id='main-content']/div[1]/div[1]")
        except Exception as ex:
            tag_list = None
        
        if not isinstance(tag_list, list) or len(tag_list) <= 0:
            parser.close()
            return pages

        paginator: AdvancedTag = tag_list[0]
        if not isinstance(paginator, AdvancedTag) or paginator.tagName.lower() != 'div' or paginator.className != 'pagination clearfix':
            parser.close()
            return pages

        num: int = 0
        text: str = ''
        child: AdvancedTag = None

        for child in paginator.childNodes:
            if child.innerText is None:
                continue
            text = child.innerText.strip(' \r\n\t')
            if not text.isnumeric():
                continue
            num = int(text)
            if num > pages:
                pages = num

        return pages

    def _parse_books(self, cat: Category, page: int = 1):
        if not isinstance(cat, Category):
            return []
        if cat.pages <= 0:
            return []
        
        response: requests.Response = None
        url: str = f'{cat.url}/page/{page}'
        req_config: dict = None
        if isinstance(self._config, dict):
            req_config = self._config.get('requests', {})
        verify: bool = req_config.get('verify', True)
        proxies: dict = req_config.get('proxies', None)
        
        try:
            response = requests.get(url, proxies=proxies, verify=verify, timeout=3)
        except Exception as ex:
            print(f'Exception: {ex}')
            return []
        
        if response.status_code != 200:
            print(f'response.status_code: {response.status_code}')
            return []
        
        parser: AdvancedHTMLParser = AdvancedHTMLParser()
        try:
            parser.parseStr(response.text)
        except MultipleRootNodeException:
            pass
        except Exception as ex:
            print(f'Exception: {ex}')
            response.close()
            return  []
        
        response.close()
        body: AdvancedTag = parser.body
        if not isinstance(body, AdvancedTag):
            print(f'Body is not AdvancedTag')
            parser.close()
            return []
        
        books: list = []

        tag_list: list = None
        try:
            tag_list = body.getElementsByXPath("//div[@class='main-content-inner clearfix']")
        except Exception as ex:
            tag_list = None
        
        if not isinstance(tag_list, list) or len(tag_list) <= 0:
            parser.close()
            return books

        container: AdvancedTag = tag_list[0]
        if not isinstance(container, AdvancedTag) or container.tagName.lower() != 'div' or container.className != 'main-content-inner clearfix':
            parser.close()
            return books

        child: AdvancedTag = None
        book_thumb: AdvancedTag = None
        book_body: AdvancedTag = None
        anchor: AdvancedTag = None
        image: AdvancedTag = None
        summary: AdvancedTag = None
        text: str = ''
        book: Book = None
        for child in container.childNodes:
            book = None
            if child.tagName.lower() !='article':
                continue

            try:
                tag_list = child.getElementsByXPath("//div[@class='entry-thumbnail hover-thumb']")
            except Exception as ex:
                tag_list = None
            
            if isinstance(tag_list, list) and len(tag_list) > 0:
                book_thumb = tag_list[0]
            
            try:
                tag_list = child.getElementsByXPath("//div[@class='entry-body']")
            except Exception as ex:
                tag_list = None
            if isinstance(tag_list, list) and len(tag_list) > 0:
                book_body = tag_list[0]
            
            if isinstance(book_thumb, AdvancedTag):
                anchor = book_thumb.firstElementChild
                if isinstance(anchor, AdvancedTag) and anchor.tagName.lower() == 'a':
                    text = anchor.getAttribute('href')
                    if isinstance(text, str):
                        if book is None:
                            book = Book(text.strip(' \r\n\t'))
                            books.append(book)
                    if book is not None:
                        image = anchor.firstElementChild
                        if isinstance(image, AdvancedTag):
                            text = image.getAttribute('src')
                            if isinstance(text, str):
                                book.image = text.strip(' \r\n\t')
                            text = image.getAttribute('alt')
                            if isinstance(text, str):
                                book.title = html2text(unquote(text)).strip(' \r\n\t')
            if book is not None:                        
                if isinstance(book_body, AdvancedTag):
                    summary = book_body.lastElementChild
                    if isinstance(summary, AdvancedTag) and summary.tagName.lower() == 'div' and summary.className.lower() == 'entry-summary':
                        if summary.hasChildNodes():
                            paragraph: AdvancedTag = summary.firstElementChild
                            if isinstance(paragraph, AdvancedTag):
                                text = paragraph.innerText
                        else:
                            text = summary.innerText
                        if isinstance(text, str):
                            book.brief = html2text(unquote(text)).strip(' \r\n\t')
            #
        return books

    def _browse_book(self, book: Book) -> bool:
        if not isinstance(book, Book):
            return False

        if not isinstance(book.url, str) or len(book.url) <= 0:
            return False
        
        response: requests.Response = None
        req_config: dict = None
        if isinstance(self._config, dict):
            req_config = self._config.get('requests', {})
        verify: bool = req_config.get('verify', True)
        proxies: dict = req_config.get('proxies', None)
        
        try:
            response = requests.get(book.url, proxies=proxies, verify=verify, timeout=3)
        except Exception as ex:
            print(f'Exception: {ex}')
            return False
        
        if response.status_code != 200:
            print(f'response.status_code: {response.status_code}')
            return False
        
        parser: AdvancedHTMLParser = AdvancedHTMLParser()
        try:
            parser.parseStr(response.text)
        except MultipleRootNodeException:
            pass
        except Exception as ex:
            print(f'Exception: {ex}')
            response.close()
            return  False
        
        response.close()
        body: AdvancedTag = parser.body
        if not isinstance(body, AdvancedTag):
            print(f'Body is not AdvancedTag')
            parser.close()
            return False

        tag_list: list = None
        try:
            tag_list = body.getElementsByXPath("//main[@id='main-content']")
        except Exception as ex:
            tag_list = None
        
        if not isinstance(tag_list, list) or len(tag_list) <= 0:
            parser.close()
            return False

        container: AdvancedTag = tag_list[0]
        if not isinstance(container, AdvancedTag) or container.tagName.lower() != 'main' or container.getAttribute('id') != 'main-content':
            parser.close()
            return False

        main_content: AdvancedTag = container.firstElementChild
        if not isinstance(main_content, AdvancedTag) or main_content.tagName.lower() != 'div' or main_content.className.lower() != 'main-content-inner clearfix':
            parser.close()
            return False

        child: AdvancedTag = None
        entry_header: AdvancedTag = None
        entry_content: AdvancedTag = None
        entry_footer: AdvancedTag = None
        anchor: AdvancedTag = None
        image: AdvancedTag = None
        summary: AdvancedTag = None
        entry_meta: AdvancedTag = None
        book_detail: AdvancedTag = None
        dl: AdvancedTag = None
        dt: AdvancedTag = None
        h1: AdvancedTag = None
        node: AdvancedTag = None
        text: str = ''
        result: bool = False
        key: str = ''
        for child in main_content.childNodes:
            if child.tagName.lower() !='article':
                continue

            try:
                tag_list = child.getElementsByXPath("//header[@class='entry-header']")
            except Exception as ex:
                tag_list = None
            if isinstance(tag_list, list) and len(tag_list) > 0:
                entry_header = tag_list[0]
            
            try:
                tag_list = child.getElementsByXPath("//div[@class='entry-content']")
            except Exception as ex:
                tag_list = None
            if isinstance(tag_list, list) and len(tag_list) > 0:
                entry_content = tag_list[0]
            
            try:
                tag_list = child.getElementsByXPath("//footer[@class='entry-footer clearfix']")
            except Exception as ex:
                tag_list = None
            if isinstance(tag_list, list) and len(tag_list) > 0:
                entry_footer = tag_list[0]
            
            if isinstance(entry_header, AdvancedTag):
                try:
                    tag_list = entry_header.getElementsByXPath("//h1[@class='single-title']")
                except Exception as ex:
                    tag_list = None
                if isinstance(tag_list, list) and len(tag_list) > 0:
                    h1 = tag_list[0]
                else:
                    h1 = None
                if isinstance(h1, AdvancedTag) and h1.tagName.lower() == 'h1' and h1.className.lower() == 'single-title':
                    if isinstance(h1.innerText, str):
                        text = h1.innerText.strip(' \r\n\t')
                        if book.title is None or len(book.title) <= 0:
                            book.title = html2text(unquote(text))
                            result = True
                
                try:
                    tag_list = entry_header.getElementsByXPath("//div[@class='entry-meta clearfix']")
                except Exception as ex:
                    tag_list = None
                if isinstance(tag_list, list) and len(tag_list) > 0:
                    entry_meta = tag_list[0]
                else:
                    entry_meta = None
                if isinstance(entry_meta, AdvancedTag) and entry_meta.tagName.lower() == 'div' and entry_meta.className.lower() == 'entry-meta clearfix':
                    try:
                        tag_list = entry_meta.getElementsByXPath("//div[@class='book-detail']")
                    except Exception as ex:
                        tag_list = None
                    if isinstance(tag_list, list) and len(tag_list) > 0:
                        book_detail = tag_list[0]
                    else:
                        book_detail = None
                
                if isinstance(book_detail, AdvancedTag) and book_detail.tagName.lower() == 'div' and book_detail.className.lower() == 'book-detail':
                    dl = book_detail.firstElementChild
                    if isinstance(dl, AdvancedTag) and dl.tagName.lower() == 'dl':
                        for node in dl.childNodes:
                            if node.tagName.lower() == 'dt':
                                if isinstance(node.innerText, str):
                                    key = node.innerText.strip(' \r\n\t').lower()
                                else:
                                    key = ''
                            elif node.tagName.lower() == 'dd':
                                if node.hasChildNodes() and isinstance(node.firstElementChild, AdvancedTag):
                                    text = node.firstElementChild.innerText
                                else:
                                    text = node.innerText
                                if isinstance(text, str):
                                    text = text.strip(' \r\n\t')
                                else:
                                    text = ''
                                if key == 'author:':
                                    authors: list = text.split(',')
                                    book.authors = authors
                                elif key == 'isbn-10:':
                                    book.isbn = text
                                elif key == 'year:':
                                    if text.isnumeric():
                                        book.published = int(text)
                                elif key == 'pages:':
                                    if text.isnumeric():
                                        book.pages = int(text)
                                elif key == 'category:':
                                    categories: list = text.split(',')
                                    book.categories = categories

            if isinstance(entry_content, AdvancedTag):
                pass

            if isinstance(entry_footer, AdvancedTag):
                try:
                    tag_list = entry_footer.getElementsByXPath("//div[@class='entry-meta clearfix']")
                except Exception as ex:
                    tag_list = None
                if isinstance(tag_list, list) and len(tag_list) > 0:
                    entry_meta = tag_list[0]
                else:
                    entry_meta = None
                
                if isinstance(entry_meta, AdvancedTag) and entry_meta.tagName.lower() == 'div' and entry_meta.className.lower() == 'entry-meta clearfix':
                    for node in entry_meta.childNodes:
                        if node.tagName.lower() != 'span' or node.className.lower() != 'download-links':
                            continue
                        anchor = node.firstElementChild
                        if isinstance(anchor, AdvancedTag) and anchor.tagName.lower() == 'a':
                            link: str = anchor.getAttribute('href')
                            if isinstance(link, str) and len(link) > 0:
                                link = link.strip(' \r\n\t')
                            text = anchor.innerText
                            if isinstance(text, str) and len(text) > 0:
                                text = text.strip(' \r\n\t')
                                formats: list = text.split(' ')
                                format: str = ''
                                if len(formats) > 0:
                                    format = formats[-1:][0]
                                else:
                                    format = text
                                if len(format) > 0:
                                    if not isinstance(book.media, dict):
                                        book.media = dict()
                                    book.media[format] = link
            #
        return result
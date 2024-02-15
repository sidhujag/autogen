import os
import requests
import re
import markdownify
import io
import uuid
import mimetypes
import json
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union, Tuple
from autogen.serper_utils import WebSearchSerperWrapper

# Optional PDF support
IS_PDF_CAPABLE = False
try:
    import pdfminer
    import pdfminer.high_level

    IS_PDF_CAPABLE = True
except ModuleNotFoundError:
    pass

# Other optional dependencies
try:
    import pathvalidate
except ModuleNotFoundError:
    pass


class SimpleTextBrowser:
    """(In preview) An extremely simple text-based web browser comparable to Lynx. Suitable for Agentic use."""
    pickle_file: str = None
    def __init__(
        self,
        start_page: Optional[str] = None,
        viewport_size: Optional[int] = 1024 * 8,
        downloads_folder: Optional[Union[str, None]] = None,
        bing_api_key: Optional[Union[str, None]] = None,
        request_kwargs: Optional[Union[Dict[str, Any], None]] = None,
        current_session_id: Optional[str] = None
    ):
        self.start_page: str = start_page if start_page else "about:blank"
        self.viewport_size = viewport_size  # Applies only to the standard uri types
        self.downloads_folder = downloads_folder
        self.history: List[str] = list()
        self.page_title: Optional[str] = None
        self.viewport_current_page = 0
        self.viewport_pages: List[Tuple[int, int]] = list()
        self.bing_api_key = bing_api_key
        self.set_address(self.start_page)
        self.request_kwargs = request_kwargs

        self._page_content = ""
        self.current_session_id = current_session_id
        self.pickle_file = f"simple_text_browser_session_{self.current_session_id}.pkl"
        self._load_state()
        
            
    
    def _load_state(self):
        if self.pickle_file:
            try:
                with open(self.pickle_file, 'r') as f:
                    state = json.load(f)
                    self.history = state['history']
                    self.page_title = state['page_title']
                    self.viewport_current_page = state['viewport_current_page']
                    self.viewport_pages = state['viewport_pages']
                    self._page_content = state['page_content']
            except (FileNotFoundError, json.JSONDecodeError):
                print(f'Could not deserialize from file {self.pickle_file}, might not exist yet...')

    def _save_state(self):
        if self.pickle_file:
            state = {
                'history': self.history,
                'page_title': self.page_title,
                'viewport_current_page': self.viewport_current_page,
                'viewport_pages': self.viewport_pages,
                'page_content': self._page_content
            }
            if os.path.exists(self.pickle_file):
                os.remove(self.pickle_file)
            with open(self.pickle_file, 'w') as f:
                try:
                    json.dump(state, f)
                except Exception as e:
                    print(f'Could not serialize file {self.pickle_file}, Exception: {str(e)}')

    @property
    def address(self) -> str:
        """Return the address of the current page."""
        return self.history[-1]

    def set_address(self, uri_or_path: str, category: Optional[str] = None):
        self.history.append(uri_or_path)

        # Handle special URIs
        if uri_or_path == "about:blank":
            self._set_page_content("")
        elif uri_or_path.startswith("bing:"):
            self._bing_search(uri_or_path[len("bing:") :].strip(), category)
        elif uri_or_path.startswith("google:"):
            self._google_search(uri_or_path[len("google:") :].strip(), category)
        else:
            if not uri_or_path.startswith("http:") and not uri_or_path.startswith("https:"):
                uri_or_path = urljoin(self.address, uri_or_path)
                self.history[-1] = uri_or_path  # Update the address with the fully-qualified path
            self._fetch_page(uri_or_path)

        self.viewport_current_page = 0
        self._save_state()

    @property
    def viewport(self) -> str:
        """Return the content of the current viewport."""
        bounds = self.viewport_pages[self.viewport_current_page]
        return self.page_content[bounds[0] : bounds[1]]

    @property
    def page_content(self) -> str:
        """Return the full contents of the current page."""
        return self._page_content

    def _set_page_content(self, content: str) -> None:
        """Sets the text content of the current page."""
        self._page_content = content
        self._split_pages()
        if self.viewport_current_page >= len(self.viewport_pages):
            self.viewport_current_page = len(self.viewport_pages) - 1


    def page_down(self) -> None:
        self.viewport_current_page = min(self.viewport_current_page + 1, len(self.viewport_pages) - 1)
        self._save_state()

    def page_up(self) -> None:
        self.viewport_current_page = max(self.viewport_current_page - 1, 0)
        self._save_state()

    def visit_page(self, path_or_uri: str, category: Optional[str] = None):
        """Update the address, visit the page, and return the content of the viewport."""
        self.set_address(path_or_uri, category)
        return self.viewport

    def _split_pages(self) -> None:
        # Split only regular pages
        if not self.address.startswith("http:") and not self.address.startswith("https:"):
            self.viewport_pages = [(0, len(self._page_content))]
            return

        # Handle empty pages
        if len(self._page_content) == 0:
            self.viewport_pages = [(0, 0)]
            return

        # Break the viewport into pages
        self.viewport_pages = []
        start_idx = 0
        while start_idx < len(self._page_content):
            end_idx = min(start_idx + self.viewport_size, len(self._page_content))  # type: ignore[operator]
            # Adjust to end on a space
            while end_idx < len(self._page_content) and self._page_content[end_idx - 1] not in [" ", "\t", "\r", "\n"]:
                end_idx += 1
            self.viewport_pages.append((start_idx, end_idx))
            start_idx = end_idx

    def _bing_api_call(self, query: str) -> Dict[str, Dict[str, List[Dict[str, Union[str, Dict[str, str]]]]]]:
        # Make sure the key was set
        if self.bing_api_key is None:
            raise ValueError("Missing Bing API key.")

        # Prepare the request parameters
        request_kwargs = self.request_kwargs.copy() if self.request_kwargs is not None else {}

        if "headers" not in request_kwargs:
            request_kwargs["headers"] = {}
        request_kwargs["headers"]["Ocp-Apim-Subscription-Key"] = self.bing_api_key

        if "params" not in request_kwargs:
            request_kwargs["params"] = {}
        request_kwargs["params"]["q"] = query
        request_kwargs["params"]["textDecorations"] = False
        request_kwargs["params"]["textFormat"] = "raw"

        request_kwargs["stream"] = False

        # Make the request
        response = requests.get("https://api.bing.microsoft.com/v7.0/search", **request_kwargs)
        response.raise_for_status()
        results = response.json()

        return results  # type: ignore[no-any-return]

    def _bing_search(self, query: str, category: Optional[str] = None):
        search_str = ""
        if category:
            search_str = f'{category}: {query}'
        else:
            search_str = query

        results = self._bing_api_call(search_str)

        web_snippets: List[str] = list()
        idx = 0
        for page in results["webPages"]["value"]:
            idx += 1
            web_snippets.append(f"{idx}. [{page['name']}]({page['url']})\n{page['snippet']}")
            if "deepLinks" in page:
                for dl in page["deepLinks"]:
                    idx += 1
                    web_snippets.append(
                        f"{idx}. [{dl['name']}]({dl['url']})\n{dl['snippet'] if 'snippet' in dl else ''}"  # type: ignore[index]
                    )

        news_snippets = list()
        if "news" in results:
            for page in results["news"]["value"]:
                idx += 1
                news_snippets.append(f"{idx}. [{page['name']}]({page['url']})\n{page['description']}")

        self.page_title = f"{query} - Search"

        content = (
            f"A Bing search for '{query}' found {len(web_snippets) + len(news_snippets)} results:\n\n## Web Results\n"
            + "\n\n".join(web_snippets)
        )
        if len(news_snippets) > 0:
            content += "\n\n## News Results:\n" + "\n\n".join(news_snippets)
        self._set_page_content(content)

    def _google_search(self, query, category: Optional[str] = None):
        search_str = ""
        if not category:
            category = "search"
        if category == "sports" or category == "events":
            search_str = f'{category}: {query}'
            category = "search"
        else:
            search_str = query
        results = WebSearchSerperWrapper.run([search_str], 15, category)
        self.page_title = f"{query} - Search"

        content = (
            f"A Google search for '{query}'. results:\n\n## Web Results\n\n{results}"
        )
        self._set_page_content(content)
        
    def _fetch_page(self, url):
        try:
            # Prepare the request parameters
            request_kwargs = self.request_kwargs.copy() if self.request_kwargs is not None else {}
            request_kwargs["stream"] = True

            # Send a HTTP request to the URL
            response = requests.get(url, **request_kwargs)
            response.raise_for_status()

            # If the HTTP request returns a status code 200, proceed
            if response.status_code == 200:
                content_type = response.headers.get("content-type", "")
                for ct in ["text/html", "text/plain", "application/pdf"]:
                    if ct in content_type.lower():
                        content_type = ct
                        break

                if content_type == "text/html":
                    # Get the content of the response
                    html = ""
                    for chunk in response.iter_content(chunk_size=512, decode_unicode=True):
                        html += chunk

                    soup = BeautifulSoup(html, "html.parser")

                    # Remove javascript and style blocks
                    for script in soup(["script", "style"]):
                        script.extract()

                    # Convert to markdown -- Wikipedia gets special attention to get a clean version of the page
                    if url.startswith("https://en.wikipedia.org/"):
                        body_elm = soup.find("div", {"id": "mw-content-text"})
                        title_elm = soup.find("span", {"class": "mw-page-title-main"})

                        if body_elm:
                            # What's the title
                            main_title = soup.title.string
                            if title_elm and len(title_elm) > 0:
                                main_title = title_elm.string
                            webpage_text = (
                                "# " + main_title + "\n\n" + markdownify.MarkdownConverter().convert_soup(body_elm)
                            )
                        else:
                            webpage_text = markdownify.MarkdownConverter().convert_soup(soup)
                    else:
                        webpage_text = markdownify.MarkdownConverter().convert_soup(soup)

                    # Convert newlines
                    webpage_text = re.sub(r"\r\n", "\n", webpage_text)

                    # Remove excessive blank lines
                    self.page_title = soup.title.string
                    self._set_page_content(re.sub(r"\n{2,}", "\n\n", webpage_text).strip())
                elif content_type == "text/plain":
                    # Get the content of the response
                    plain_text = ""
                    for chunk in response.iter_content(chunk_size=512, decode_unicode=True):
                        plain_text += chunk

                    self.page_title = None
                    self._set_page_content(plain_text)
                elif IS_PDF_CAPABLE and content_type == "application/pdf":
                    pdf_data = io.BytesIO(response.raw.read())
                    self.page_title = None
                    self._set_page_content(pdfminer.high_level.extract_text(pdf_data))
                elif self.downloads_folder is not None:
                    # Try producing a safe filename
                    fname = None
                    try:
                        fname = pathvalidate.sanitize_filename(os.path.basename(urlparse(url).path)).strip()
                    except NameError:
                        pass

                    # No suitable name, so make one
                    if fname is None:
                        extension = mimetypes.guess_extension(content_type)
                        if extension is None:
                            extension = ".download"
                        fname = str(uuid.uuid4()) + extension

                    # Open a file for writing
                    download_path = os.path.abspath(os.path.join(self.downloads_folder, fname))
                    with open(download_path, "wb") as fh:
                        for chunk in response.iter_content(chunk_size=512):
                            fh.write(chunk)

                    # Return a page describing what just happened
                    self.page_title = "Download complete."
                    self._set_page_content(f"Downloaded '{url}' to '{download_path}'.")
                else:
                    self.page_title = f"Error - Unsupported Content-Type '{content_type}'"
                    self._set_page_content(self.page_title)
            else:
                self.page_title = "Error"
                self._set_page_content("Failed to retrieve " + url)
        except requests.exceptions.RequestException as e:
            self.page_title = "Error"
            self._set_page_content(str(e))

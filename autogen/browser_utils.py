# ruff: noqa: E722
import os
import requests
import traceback
import re
import markdownify
import io
import uuid
import mimetypes
import json
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union, Tuple
from autogen.serper_utils import WebSearchSerperWrapper
from pathlib import Path

# Optional PDF support
IS_PDF_CAPABLE = False
try:
    import pdfminer
    import pdfminer.high_level

    IS_PDF_CAPABLE = True
except ModuleNotFoundError:
    pass

# Optional YouTube transcription support
IS_YOUTUBE_TRANSCRIPT_CAPABLE = False
try:
    from youtube_transcript_api import YouTubeTranscriptApi

    IS_YOUTUBE_TRANSCRIPT_CAPABLE = True
except ModuleNotFoundError:
    pass

# Other optional dependencies
try:
    import pathvalidate
except ModuleNotFoundError:
    pass

# The Selenium package is used to automate web browser interaction from Python
IS_SELENIUM_CAPABLE = False
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.edge.options import Options as EdgeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.chrome.options import Options as ChromeOptions

    IS_SELENIUM_CAPABLE = True
except ImportError as e:
    print(f"The module/package '{e.name}' is not available.")
    print("Try running 'pip install selenium'.  You may need to run 'sudo easy_install selenium' on Linux or MacOS")
    print(
        "Official selenium installation documentation: https://www.selenium.dev/documentation/webdriver/getting_started/install_library/"
    )
    raise e


class TextRendererResult:
    """The result of rendering a webpage to text."""

    def __init__(self, title: Union[str, None] = None, page_content: str = ""):
        self.title = title
        self.page_content = page_content


class PageTextRenderer:
    """A TextRender is used by the SimpleTextBrowser to claim
    responsibility for rendering a page. Once a page has been claimed,
    the instance' render_page function will be called, and the result
    stream is expected to be consumed -- there is no going back."""

    def claim_responsibility(self, url, status_code, content_type, **kwargs) -> bool:
        """Return true only if the text renderer is prepared to
        claim responsibility for the page.
        """
        raise NotImplementedError()

    def render_page(self, response, url, status_code, content_type) -> TextRendererResult:
        """Return true only if the text renderer is prepared to
        claim responsibility for the page.
        """
        raise NotImplementedError()

    # Helper functions
    def _read_all_text(self, response) -> str:
        """Read the entire response, and return as a string."""
        text = ""
        for chunk in response.iter_content(chunk_size=512, decode_unicode=True):
            text += chunk
        return text

    def _read_all_html(self, response) -> BeautifulSoup:
        """Read the entire response, and return as a beautiful soup object."""
        return BeautifulSoup(self._read_all_text(response), "html.parser")

    def _read_all_bytesio(self, response) -> io.BytesIO:
        """Read the entire response, and return an in-memory bytes stream."""
        return io.BytesIO(response.raw.read())

    def _fix_newlines(self, rendered_text) -> str:
        re.sub(r"\r\n", "\n", rendered_text)
        return re.sub(r"\n{2,}", "\n\n", rendered_text).strip()  # Remove excessive blank lines


class PlainTextRenderer(PageTextRenderer):
    """Anything with content type text/plain"""

    def claim_responsibility(self, url, status_code, content_type, **kwargs) -> bool:
        return content_type is not None and "text/plain" in content_type.lower()

    def render_page(self, response, url, status_code, content_type) -> TextRendererResult:
        return TextRendererResult(title=None, page_content=self._fix_newlines(self._read_all_text(response)))


class HtmlRenderer(PageTextRenderer):
    """Anything with content type text/html"""

    def claim_responsibility(self, url, status_code, content_type, **kwargs) -> bool:
        return content_type is not None and "text/html" in content_type.lower()

    def render_page(self, response, url, status_code, content_type) -> TextRendererResult:
        soup = self._read_all_html(response)

        # Remove javascript and style blocks
        for script in soup(["script", "style"]):
            script.extract()

        webpage_text = markdownify.MarkdownConverter().convert_soup(soup)

        return TextRendererResult(
            title=soup.title.string,
            page_content=self._fix_newlines(webpage_text),
        )


class WikipediaRenderer(PageTextRenderer):
    """Handle Wikipedia pages separately, focusing only on the main document content."""

    def claim_responsibility(self, url, status_code, content_type, **kwargs) -> bool:
        return bool(
            content_type is not None
            and "text/html" in content_type.lower()
            and re.search(r"^https?:\/\/[a-zA-Z]{2,3}\.wikipedia.org\/", url)
        )

    def render_page(self, response, url, status_code, content_type) -> TextRendererResult:
        soup = self._read_all_html(response)

        # Remove javascript and style blocks
        for script in soup(["script", "style"]):
            script.extract()

        # Print only the main content
        body_elm = soup.find("div", {"id": "mw-content-text"})
        title_elm = soup.find("span", {"class": "mw-page-title-main"})

        webpage_text = ""
        if body_elm:
            # What's the title
            main_title = soup.title.string
            if title_elm and len(title_elm) > 0:
                main_title = title_elm.string

            # Render the page
            webpage_text = "# " + main_title + "\n\n" + markdownify.MarkdownConverter().convert_soup(body_elm)
        else:
            webpage_text = markdownify.MarkdownConverter().convert_soup(soup)

        return TextRendererResult(
            title=soup.title.string,
            page_content=self._fix_newlines(webpage_text),
        )


class YouTubeRenderer(PageTextRenderer):
    """Handle YouTube specially, focusing on the video title, description, and transcript."""

    def claim_responsibility(self, url, status_code, content_type, **kwargs) -> bool:
        return (
            content_type is not None
            and "text/html" in content_type.lower()
            and url.startswith("https://www.youtube.com/watch?")
        )

    def render_page(self, response, url, status_code, content_type) -> TextRendererResult:
        soup = self._read_all_html(response)

        # Read the meta tags
        metadata = {"title": soup.title.string}
        for meta in soup(["meta"]):
            for a in meta.attrs:
                if a in ["itemprop", "property", "name"]:
                    metadata[meta[a]] = meta.get("content", "")
                    break

        # We can also try to read the full description. This is more prone to breaking, since it reaches into the page implementation
        try:
            for script in soup(["script"]):
                content = script.text
                if "ytInitialData" in content:
                    lines = re.split(r"\r?\n", content)
                    obj_start = lines[0].find("{")
                    obj_end = lines[0].rfind("}")
                    if obj_start >= 0 and obj_end >= 0:
                        data = json.loads(lines[0][obj_start : obj_end + 1])
                        attrdesc = self._findKey(data, "attributedDescriptionBodyText")
                        if attrdesc:
                            metadata["description"] = attrdesc["content"]
                    break
        except:
            pass

        # Start preparing the page
        webpage_text = "# YouTube\n"

        title = self._get(metadata, ["title", "og:title", "name"])
        if title:
            webpage_text += f"\n## {title}\n"

        stats = ""
        views = self._get(metadata, ["interactionCount"])
        if views:
            stats += f"- **Views:** {views}\n"

        keywords = self._get(metadata, ["keywords"])
        if keywords:
            stats += f"- **Keywords:** {keywords}\n"

        runtime = self._get(metadata, ["duration"])
        if runtime:
            stats += f"- **Runtime:** {runtime}\n"

        if len(stats) > 0:
            webpage_text += f"\n### Video Metadata\n{stats}\n"

        description = self._get(metadata, ["description", "og:description"])
        if description:
            webpage_text += f"\n### Description\n{description}\n"

        if IS_YOUTUBE_TRANSCRIPT_CAPABLE:
            transcript_text = ""
            parsed_url = urlparse(url)
            params = parse_qs(parsed_url.query)
            if "v" in params:
                video_id = params["v"][0]
                try:
                    # Must be a single transcript.
                    transcript = YouTubeTranscriptApi.get_transcript(video_id)
                    transcript_text = " ".join([part["text"] for part in transcript])
                    # Alternative formatting:
                    # formatter = TextFormatter()
                    # formatter.format_transcript(transcript)
                except:
                    pass
            if transcript_text:
                webpage_text += f"\n### Transcript\n{transcript_text}\n"

        return TextRendererResult(
            title="",
            page_content=self._fix_newlines(webpage_text),
        )

    def _get(self, json, keys, default=None):
        for k in keys:
            if k in json:
                return json[k]
        return default

    def _findKey(self, json, key):
        if isinstance(json, list):
            for elm in json:
                ret = self._findKey(elm, key)
                if ret is not None:
                    return ret
        elif isinstance(json, dict):
            for k in json:
                if k == key:
                    return json[k]
                else:
                    ret = self._findKey(json[k], key)
                    if ret is not None:
                        return ret
        return None


class PdfRenderer(PageTextRenderer):
    """Anything with content type application/pdf"""

    def claim_responsibility(self, url, status_code, content_type, **kwargs) -> bool:
        return content_type is not None and "application/pdf" in content_type.lower()

    def render_page(self, response, url, status_code, content_type) -> TextRendererResult:
        return TextRendererResult(
            title=None,
            page_content=pdfminer.high_level.extract_text(self._read_all_bytesio(response)),
        )


class DownloadRenderer(PageTextRenderer):
    def __init__(self, browser):
        self._browser = browser

    """Catch all downloader, when a download folder is set."""

    def claim_responsibility(self, url, status_code, content_type, **kwargs) -> bool:
        return bool(self._browser.downloads_folder)

    def render_page(self, response, url, status_code, content_type) -> TextRendererResult:
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
        download_path = os.path.abspath(os.path.join(self._browser.downloads_folder, fname))
        with open(download_path, "wb") as fh:
            for chunk in response.iter_content(chunk_size=512):
                fh.write(chunk)

        return TextRendererResult(
            title="Download complete.",
            page_content=f"Downloaded '{url}' to '{download_path}'.",
        )


class FallbackPageRenderer(PageTextRenderer):
    """Accept all requests that come to it."""

    def claim_responsibility(self, url, status_code, content_type, **kwargs) -> bool:
        return True

    def render_page(self, response, url, status_code, content_type) -> TextRendererResult:
        return TextRendererResult(
            title=f"Error - Unsupported Content-Type '{content_type}'",
            page_content=f"Error - Unsupported Content-Type '{content_type}'",
        )


class FallbackErrorRenderer(PageTextRenderer):
    def __init__(self):
        self._html_renderer = HtmlRenderer()

    """Accept all requests that come to it."""

    def claim_responsibility(self, url, status_code, content_type, **kwargs) -> bool:
        return True

    def render_page(self, response, url, status_code, content_type) -> TextRendererResult:
        # If the error was rendered in HTML we might as well render it
        if content_type is not None and "text/html" in content_type.lower():
            res = self._html_renderer.render_page(response, url, status_code, content_type)
            res.title = f"Error {status_code}"
            res.page_content = f"## Error {status_code}\n\n{res.page_content}"
            return res
        else:
            return TextRendererResult(
                title=f"Error {status_code}",
                page_content=f"## Error {status_code}\n\n{self._read_all_text(response)}",
            )

class SimpleTextBrowser:
    """(In preview) An extremely simple text-based web browser comparable to Lynx. Suitable for Agentic use."""
    _path_to_data_file: str = None
    def __init__(
        self,
        start_page: Optional[str] = None,
        viewport_size: Optional[int] = 1024 * 8,
        downloads_folder: Optional[Union[str, None]] = None,
        bing_api_key: Optional[Union[str, None]] = None,
        request_kwargs: Optional[Union[Dict[str, Any], None]] = None,
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
        self._page_renderers: List[PageTextRenderer] = []
        self._error_renderers: List[PageTextRenderer] = []
        self._page_content: str = ""

        self._find_on_page_query: Union[str, None] = None
        self._find_on_page_last_result: Union[int, None] = None  # Location of the last result

        # Register renderers for successful browsing operations
        # Later registrations are tried first / take higher priority than earlier registrations
        # To this end, the most specific renderers should appear below the most generic renderers
        self.register_page_renderer(FallbackPageRenderer())
        self.register_page_renderer(DownloadRenderer(self))
        self.register_page_renderer(HtmlRenderer())
        self.register_page_renderer(PlainTextRenderer())
        self.register_page_renderer(WikipediaRenderer())
        self.register_page_renderer(YouTubeRenderer())

        if IS_PDF_CAPABLE:
            self.register_page_renderer(PdfRenderer())

        # Register renderers for error conditions
        self.register_error_renderer(FallbackErrorRenderer())
        self._page_content = ""

    
    def load_state(self, path_to_data_dir: Path):
        self._path_to_data_file = path_to_data_dir / "simple_text_browser_session.pkl"
        try:
            if self._path_to_data_file.exists():
                with open(self._path_to_data_file, 'r') as f:
                    state = json.load(f)
                    self.history = state['history']
                    self.page_title = state['page_title']
                    self.viewport_current_page = state['viewport_current_page']
                    self.viewport_pages = state['viewport_pages']
                    self._page_content = state['page_content']
                    self.find_on_page_query = state['find_on_page_query']
                    self.find_on_page_viewport = state['find_on_page_viewport']
        except (FileNotFoundError, json.JSONDecodeError):
            print(f'Could not deserialize from file {self._path_to_data_file}, might not exist yet...')

    def save_state(self):
        if self._path_to_data_file:
            self._path_to_data_file.parent.mkdir(parents=True, exist_ok=True)
            state = {
                'history': self.history,
                'page_title': self.page_title,
                'viewport_current_page': self.viewport_current_page,
                'viewport_pages': self.viewport_pages,
                'page_content': self._page_content,
                'find_on_page_query': self.find_on_page_query,
                'find_on_page_viewport': self.find_on_page_viewport,
            }
            with open(self._path_to_data_file, 'w') as f:
                try:
                    json.dump(state, f)
                except Exception as e:
                    print(f'Could not serialize file {self._path_to_data_file}, Exception: {str(e)}')

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
        self.find_on_page_query = None
        self.find_on_page_viewport = None
        self.save_state()

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
        self.save_state()

    def page_up(self) -> None:
        self.viewport_current_page = max(self.viewport_current_page - 1, 0)
        self.save_state()

    def find_on_page(self, query: str) -> Union[str, None]:
        """Searches for the query from the current viewport forward, looping back to the start if necessary."""

        # Did we get here via a previous find_on_page search with the same query?
        # If so, map to find_next
        if query == self._find_on_page_query and self.viewport_current_page == self._find_on_page_last_result:
            return self.find_next()

        # Ok it's a new search start from the current viewport
        self._find_on_page_query = query
        viewport_match = self._find_next_viewport(query, self.viewport_current_page)
        if viewport_match is None:
            self._find_on_page_last_result = None
            return None
        else:
            self.viewport_current_page = viewport_match
            self._find_on_page_last_result = viewport_match
            return self.viewport

    def find_next(self) -> None:
        """Scroll to the next viewport that matches the query"""

        if self._find_on_page_query is None:
            return None

        starting_viewport = self._find_on_page_last_result
        if starting_viewport is None:
            starting_viewport = 0
        else:
            starting_viewport += 1
            if starting_viewport >= len(self.viewport_pages):
                starting_viewport = 0

        viewport_match = self._find_next_viewport(self._find_on_page_query, starting_viewport)
        if viewport_match is None:
            self._find_on_page_last_result = None
            return None
        else:
            self.viewport_current_page = viewport_match
            self._find_on_page_last_result = viewport_match
            return self.viewport

    def _find_next_viewport(self, query: str, starting_viewport: int) -> Union[int, None]:
        """Search for matches between the starting viewport looping when reaching the end."""

        if query is None:
            return None

        # Normalize the query, and convert to a regular expression
        nquery = re.sub(r"\*", "__STAR__", query)
        nquery = " " + (" ".join(re.split(r"\W+", nquery))).strip() + " "
        nquery = nquery.replace(" __STAR__ ", "__STAR__ ")  # Merge isolated stars with prior word
        nquery = nquery.replace("__STAR__", ".*").lower()

        if nquery.strip() == "":
            return None

        idxs = list()
        idxs.extend(range(starting_viewport, len(self.viewport_pages)))
        idxs.extend(range(0, starting_viewport))

        for i in idxs:
            bounds = self.viewport_pages[i]
            content = self.page_content[bounds[0] : bounds[1]]

            # TODO: Remove markdown links and images
            ncontent = " " + (" ".join(re.split(r"\W+", content))).strip().lower() + " "
            if re.search(nquery, ncontent):
                return i

        return None
    
    def visit_page(self, path_or_uri: str, category: Optional[str] = None):
        """Update the address, visit the page, and return the content of the viewport."""
        self.set_address(path_or_uri, category)
        return self.viewport

    def register_page_renderer(self, renderer: PageTextRenderer) -> None:
        """Register a page text renderer."""
        self._page_renderers.insert(0, renderer)

    def register_error_renderer(self, renderer: PageTextRenderer) -> None:
        """Register a page text renderer."""
        self._error_renderers.insert(0, renderer)

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
            category = "news"
        else:
            search_str = query
        results = WebSearchSerperWrapper.run([search_str], 15, category)
        self.page_title = f"{query} - Search"

        content = (
            f"A Google search for '{query}'. results:\n\n## Web Results\n\n{results}"
        )
        self._set_page_content(content)
        
    def _fetch_page(self, url: str) -> None:
        try:
            # Prepare the request parameters
            request_kwargs = self.request_kwargs.copy() if self.request_kwargs is not None else {}
            request_kwargs["stream"] = True

            # Send a HTTP request to the URL
            response = requests.get(url, **request_kwargs)
            response.raise_for_status()

            # If the HTTP request was successful
            content_type = response.headers.get("content-type", "")
            for renderer in self._page_renderers:
                if renderer.claim_responsibility(url, response.status_code, content_type):
                    res = renderer.render_page(response, url, response.status_code, content_type)
                    self.page_title = res.title
                    self._set_page_content(res.page_content)
                    return

            # Unhandled page
            self.page_title = "Error - Unhandled _fetch_page"
            self._set_page_content(
                f"""Error - Unhandled _fetch_page:
Url: {url}
Status code: {response.status_code}
Content-type: {content_type}"""
            )
        except requests.exceptions.RequestException as ex:
            for renderer in self._error_renderers:
                response = ex.response
                content_type = response.headers.get("content-type", "")
                if renderer.claim_responsibility(url, response.status_code, content_type):
                    res = renderer.render_page(response, url, response.status_code, content_type)
                    self.page_title = res.title
                    self._set_page_content(res.page_content)
                    return
            self.page_title = "Error - Unhandled _fetch_page"
            self._set_page_content(
                f"""Error - Unhandled _fetch_page error:
Url: {url}
Status code: {response.status_code}
Content-type: {content_type}"""
            )

                
def get_scheme(url):
    return urlparse(url).scheme if isinstance(url, str) else url.scheme


def get_domain(url):
    return urlparse(url).netloc if isinstance(url, str) else url.netloc


def get_path(url):
    return urlparse(url).path if isinstance(url, str) else url.path


def get_last_path(url):
    return os.path.basename(urlparse(url).path) if isinstance(url, str) else os.path.basename(url.path)


def get_file_path_from_url(url):  # URL to Directory function
    """
    get_file_path_from_url function: This function takes a URL as input and returns the corresponding local file path as a string.

    Parameters:
    url (str | ParseResult): The URL of the file for which the local path is to be obtained.

    Returns:
    str: The local file path on the system as a string.
    """

    # Remove any trailing forward slash
    url = url[:-1] if url[-1] == "/" else url

    # Parse the URL
    parsed_url = urlparse(url) if isinstance(url, str) else url
    canonical_url = parsed_url.netloc.replace("www.", "")

    if "github.com" in url and len(parsed_url.path.split("/")) >= 2:
        relative_path = os.path.join(canonical_url, parsed_url.path)
    elif len(parsed_url.path.split("/")) >= 1:
        relative_path = os.path.join(canonical_url, get_last_path(parsed_url))

    # Remove any preceding forward slash
    relative_path = relative_path[1:] if relative_path[0] == "/" else relative_path

    return relative_path


def fix_missing_protocol(img_url, source_url):  # Correct a url if it's missing the protocol
    """
    Fixes a URL by adding the missing protocol (http or https) based on the provided domain.

    Parameters:
    - img_url (str): The input image URL to be fixed.
    - domain (str): The domain of the image URL which is used to determine the protocol.

    Returns:
    - str: A corrected URL string with the missing protocol added.
    """

    protocol = get_scheme(source_url)
    domain = get_domain(source_url)

    if img_url.startswith("//"):  # If the URL starts with "//"
        img_url = f"{protocol}:{img_url}"  # Add "https:" before it

    elif not bool(get_domain(img_url)):  # domain not in img_url:
        img_url = f"{protocol}://{domain}/{img_url}"

    return img_url


def extract_pdf_text(local_pdf_path):  # Returns the extracted text content from a local PDF file
    """
    Extracts the text content from a local PDF file and returns it as a string.

    Parameters:
    - local_pdf_path (str): The path to the local PDF file from which the text will be extracted.

    Returns:
    - str: A string containing the text content of the provided PDF file.
    """

    try:
        text = pdfminer.high_level.extract_text(local_pdf_path)
    except Exception:
        traceback.print_exc()
        text = ""

    return text


def download_using_requests(
    driver, download_url, save_path
):  # `requests` downloads assisted by selenium webdriver cookies
    """
    This function takes a Selenium WebDriver instance, a URL to download a file, and a path where you want to save the downloaded file.

    It first retrieves cookies from the given driver, converts them into a format suitable for use with the `requests` library, and then uses these cookies to successfully download the specified file using the `requests.get()` function. The `User-Agent` header is also set to match that used by the WebDriver instance.

    Args:
        driver (webdriver.chrome.webdriver.WebDriver): A Selenium WebDriver instance, typically obtained from selenium.webdriver.Chrome() or another appropriate method for your browser of choice.
        download_url (str): The URL to the file you want to download.
        save_path (str): The path where you would like the downloaded file to be saved.

    Returns:
        None, but successfully downloads a file from the given URL using the cookies and headers obtained from the WebDriver instance.

    Raises:
        Exception: If the file cannot be downloaded due to an error in the `requests.get()` call.
    """

    def get_cookies(driver):
        return driver.get_cookies()

    def convert_cookies_to_requests_format(cookies):
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie["name"]] = cookie["value"]
        return cookie_dict

    def download_file_with_cookies(url, session_cookies, save_path, user_agent=None):
        headers = {
            "User-Agent": user_agent
            if user_agent
            else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

        response = requests.get(url, cookies=session_cookies, headers=headers, stream=True)
        if response.status_code == 200:
            with open(save_path, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)

    # Extract cookies from WebDriver
    cookies = get_cookies(driver)

    # Convert cookies for use with requests
    session_cookies = convert_cookies_to_requests_format(cookies)

    # Define the user-agent if you want to match the one used by your WebDriver
    user_agent = driver.execute_script("return navigator.userAgent;")

    # Download file using requests with the same session cookies and headers
    download_file_with_cookies(download_url, session_cookies, save_path, user_agent=user_agent)


def SeleniumBrowser(**kwargs):  # Function that loads the web driver
    """
    This function launches a headless Selenium browser based on the specified 'browser'. The available options are 'edge', 'firefox', and 'chrome'.

    Parameters:
        browser (str): A string specifying which browser to launch. Defaults to 'firefox'.
        download_dir (str): A path to where downloaded files are stored.  Defaults to None

    Returns:
        webdriver: An instance of the Selenium WebDriver based on the specified browser.  User can open a new page by `webdriver.get('https://www.microsoft.com')`.

    Raises:
        ImportError: If selenium package is not installed, it raises an ImportError with a message suggesting to install it using pip.
    """

    # Load the arguments from kwargs
    browser = kwargs.get("browser", "edge")
    download_dir = kwargs.get("download_dir", None)

    def get_headless_options(download_dir, options):
        options.headless = True
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,5200")
        options.add_argument("--downloadsEnabled")
        if download_dir:
            options.set_preference("download.default_directory", download_dir)
        return options

    if browser.lower() == "edge":
        driver = webdriver.Edge(options=get_headless_options(download_dir, EdgeOptions()))
    elif browser.lower() == "firefox":
        driver = webdriver.Firefox(options=get_headless_options(download_dir, FirefoxOptions()))
    elif browser.lower() == "chrome":
        driver = webdriver.Chrome(options=get_headless_options(download_dir, ChromeOptions()))

    driver.capabilities["se:downloadsEnablead"] = True

    return driver


class SeleniumBrowserWrapper:  # A wrapper to bridge compatibility between SimpleTextBrowser and SeleniumBrowser
    """
    SeleniumBrowserWrapper class is a wrapper that manages the interaction with a Selenium web driver.
    It provides methods to control the browser, set up the viewport size, and download files.

    Parameters:
    - start_page (Optional[str]): The initial URL of the web page to load. Defaults to "about:blank".
    - viewport_size (Optional[int]): The width of the viewport in pixels. Defaults to 1024 * 8.
    - downloads_folder (Optional[Union[str, None]]): The directory where downloaded files will be saved. If set to `None`, default downloads folder will be used.
    - bing_api_key (Optional[Union[str, None]]): The API key for Bing search engine.
    - request_kwargs (Optional[Union[Dict[str, Any], None]]): Additional keyword arguments that can be passed for customization.
    - web_driver (Optional[str]): The type of web driver to use. Defaults to 'edge'.

    Attributes:
    - start_page (str): The initial URL of the web page to load.
    - viewport_size (int): The width of the viewport in pixels.
    - downloads_folder (Union[str, None]): The directory where downloaded files will be saved.
    - history (List[str]): A list containing the URLs visited by the browser.
    - page_title (Optional[str]): The title of the current web page.
    - viewport_current_page (int): The index of the current web page in relation to all pages loaded.
    - viewport_pages (List[Tuple[int, int]]): A list containing tuples of width and height for each viewed web page.
    - bing_api_key (Optional[str]): The API key for Bing search engine.
    - request_kwargs (Optional[Union[Dict[str, Any], None]]): Additional keyword arguments passed during instantiation.
    - _page_content (str): The content of the current web page.
    - driver: An instance of SeleniumBrowser class that manages the browser interaction.

    Notes:
    - Viewport Size and Pages: The concept of viewport size and pagination doesn't directly apply to Selenium as it does in a text-based browser. Selenium interacts with the whole page. However, actions like scrolling can be simulated.
    - Downloads Folder: This is handled through ChromeOptions if you need to set a default download directory.
    - History Management: This wrapper maintains a simple history of visited URLs for compatibility with the SimpleTextBrowser's API.
    - Page Content: Selenium's page_source property provides the HTML content of the current page, making the distinction between viewport and page content less relevant.

    """

    def __init__(
        self,
        start_page: Optional[str] = None,
        viewport_size: Optional[int] = 1024 * 8,
        downloads_folder: Optional[Union[str, None]] = None,
        bing_api_key: Optional[Union[str, None]] = None,
        request_kwargs: Optional[Union[Dict[str, Any], None]] = None,
        web_driver: Optional[str] = "edge",
    ):
        self.start_page: str = start_page if start_page else "about:blank"
        self.viewport_size = viewport_size  # Applies only to the standard uri types
        self.downloads_folder = downloads_folder
        self.history: List[str] = list()
        self.page_title: Optional[str] = None
        self.viewport_current_page = 0
        self.viewport_pages: List[Tuple[int, int]] = list()
        self.bing_api_key = bing_api_key
        self.request_kwargs = request_kwargs

        self._page_content = ""

        # Initialize the WebDriver
        self.driver = SeleniumBrowser(browser=web_driver, download_dir=downloads_folder)
        if start_page:
            self.set_address(self.start_page)

    @property
    def address(self) -> str:
        """Return the address of the current page."""
        return self.history[-1] if self.history else "about:blank"

    @property
    def viewport(self) -> str:
        """Return the content of the current viewport."""
        return self.driver.page_source  # Selenium directly interacts with the page, no viewport concept

    @property
    def page_content(self) -> str:
        """Return the full contents of the current page."""
        return self.viewport  # In Selenium, viewport essentially contains the full page content

    def set_address(self, uri_or_path: str) -> None:
        """Navigate to a given URI and update history."""
        if not uri_or_path.startswith("http:") and not uri_or_path.startswith("https:"):
            uri_or_path = urljoin(self.address, uri_or_path)
        self.driver.get(uri_or_path)
        self.history.append(uri_or_path)
        self._update_page_content()

    def visit_page(self, path_or_uri: str) -> str:
        """Navigate to a page and return its content."""
        self.set_address(path_or_uri)
        return self.viewport

    def page_down(self) -> None:
        """Simulate page down action."""
        # Simulate pressing Page Down key
        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)

    def page_up(self) -> None:
        """Simulate page up action."""
        # Simulate pressing Page Up key
        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_UP)

    def _update_page_content(self) -> None:
        """Update internal content state, including page title."""
        self.page_title = self.driver.title

    def close(self):
        """Close the browser."""
        self.driver.quit()

    def _split_pages(self) -> None:
        # This is not implemented with the selenium.webdirver wrapper
        return

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

    def _bing_search(self, query: str) -> None:
        results = self._bing_api_call(query)

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

    def download(self, uri_or_path: str) -> None:  # TODO: update this based on the new method
        """Download from a given URI"""
        self.driver.get(uri_or_path)

    def _fetch_page(self, url: str) -> None:
        from selenium.common.exceptions import TimeoutException

        try:
            self.driver.get(url)
            self.page_title = self.driver.title

            # Selenium WebDriver directly accesses the rendered page,
            # so we don't need to manually fetch or process the HTML.
            # However, you can still manipulate or extract content from the page using Selenium methods.

            # Example of extracting and cleaning the page content
            if "wikipedia.org" in url:
                body_elm = self.driver.find_element(By.cssSelector, "div#mw-content-text")
                main_title = self.driver.title
                webpage_text = (
                    "# "
                    + main_title
                    + "\n\n"
                    + markdownify.MarkdownConverter().convert_soup(body_elm.get_attribute("innerHTML"))
                )
            else:
                webpage_text = self.driver.find_element(By.TAG_NAME, "body").get_attribute("innerText")

            # Convert newlines, remove excessive blank lines
            webpage_text = re.sub(r"\r\n", "\n", webpage_text)
            self._set_page_content(re.sub(r"\n{2,}", "\n\n", webpage_text).strip())

        except TimeoutException:
            self.page_title = "Error"
            self._set_page_content("Timeout while retrieving " + url)

import os
import logging
import re
from typing import Any, Dict, Optional, Tuple
from typing_extensions import Annotated
from autogen import OpenAIWrapper
from autogen.browser_utils import SimpleTextBrowser
from autogen.token_count_utils import count_token, get_max_token_limit
from dotenv import load_dotenv, find_dotenv

logger = logging.getLogger(__name__)


class WebSurferService():
    @staticmethod
    def _create_summarizer_client(summarizer_llm_config: Dict[str, Any]):
        # Create the summarizer client
        summarization_client = None if summarizer_llm_config is False else OpenAIWrapper(**summarizer_llm_config)  # type: ignore[arg-type]
        return summarization_client
  
    # Helper functions
    @staticmethod
    def _browser_state(browser) -> Tuple[str, str]:
        header = f"Address: {browser.address}\n"
        if browser.page_title is not None:
            header += f"Title: {browser.page_title}\n"

        current_page = browser.viewport_current_page
        total_pages = len(browser.viewport_pages)

        header += f"Viewport position: Showing page {current_page+1} of {total_pages}.\n"
        return (header, browser.viewport)

    @staticmethod
    def informational_search(current_session_id: Annotated[str, "The current session ID."],
                             query: Annotated[str, "The informational web search query to perform."],
                                search_engine: Annotated[Optional[str], "[Optional] Search engine to use, 'bing' or 'google'. (Defaults to 'bing')"] = 'bing',
                                category: Annotated[Optional[str], "Category to filter search. One of 'news', 'places', 'images', 'search', 'videos', 'shopping', 'sports', 'events' (Defaults to 'search')"] = 'search') -> str:
        if search_engine != "google" and search_engine != "bing":
            return f"search engine must be either google or bing, you provided {search_engine}"
        load_dotenv(find_dotenv(usecwd=True))
        scratchdir = os.getenv('SCRATCH_DIR')
        bingkey = os.getenv('BING_API_KEY')
        if not scratchdir:
            return "Could not find SCRATCH_DIR in the environment variables!"
        if not bingkey:
            return f"Could not find BING_API_KEY in the environment variables! os environ {os.environ}"
        browser_config={"current_session_id": current_session_id, "downloads_folder": scratchdir, "bing_api_key": bingkey}
        browser = SimpleTextBrowser(**(browser_config))
        browser.visit_page(f"{search_engine}: {query}", category)
        header, content = WebSurferService._browser_state(browser)
        return header.strip() + "\n=======================\n" + content

    @staticmethod
    def navigational_search(current_session_id: Annotated[str, "The current session ID."],
                            query: Annotated[str, "The navigational web search query to perform."],
                                search_engine: Annotated[Optional[str], "[Optional] Search engine to use, 'bing' or 'google'. (Defaults to 'bing')"] = 'bing',
                                category: Annotated[Optional[str], "Category to filter search. One of 'news', 'places', 'images', 'search', 'videos', 'shopping', 'sports', 'events' (Defaults to 'search')"] = 'search') -> str:
        if search_engine != "google" and search_engine != "bing":
            return f"search engine must be either google or bing, you provided {search_engine}"
        load_dotenv(find_dotenv(usecwd=True))
        scratchdir = os.getenv('SCRATCH_DIR')
        bingkey = os.getenv('BING_API_KEY')
        if not scratchdir:
            return "Could not find SCRATCH_DIR in the environment variables!"
        if not bingkey:
            return f"Could not find BING_API_KEY in the environment variables! os environ {os.environ}"
        browser_config={"current_session_id": current_session_id, "downloads_folder": scratchdir, "bing_api_key": bingkey}
        browser = SimpleTextBrowser(**(browser_config))
        browser.visit_page(f"{search_engine}: {query}", category)

        # Extract the first link
        m = re.search(r"\[.*?\]\((http.*?)\)", browser.page_content)
        if m:
            browser.visit_page(m.group(1))

        # Return where we ended up
        header, content = WebSurferService._browser_state(browser)
        return header.strip() + "\n=======================\n" + content

    @staticmethod
    def visit_page(current_session_id: Annotated[str, "The current session ID."],
                   url: Annotated[str, "The relative or absolute url of the webapge to visit."]) -> str:
        load_dotenv(find_dotenv(usecwd=True))
        browser_config={"current_session_id": current_session_id, "downloads_folder": os.getenv('SCRATCH_DIR'), "bing_api_key": os.getenv('BING_API_KEY')}
        browser = SimpleTextBrowser(**(browser_config))
        browser.visit_page(url)
        header, content = WebSurferService._browser_state(browser)
        return header.strip() + "\n=======================\n" + content

    @staticmethod
    def page_up(current_session_id: Annotated[str, "The current session ID."]) -> str:
        load_dotenv(find_dotenv(usecwd=True))
        browser_config={"current_session_id": current_session_id, "downloads_folder": os.getenv('SCRATCH_DIR'), "bing_api_key": os.getenv('BING_API_KEY')}
        browser = SimpleTextBrowser(**(browser_config))
        browser.page_up()
        header, content = WebSurferService._browser_state(browser)
        return header.strip() + "\n=======================\n" + content

    @staticmethod
    def page_down(current_session_id: Annotated[str, "The current session ID."]) -> str:
        load_dotenv(find_dotenv(usecwd=True))
        browser_config={"current_session_id": current_session_id, "downloads_folder": os.getenv('SCRATCH_DIR'), "bing_api_key": os.getenv('BING_API_KEY')}
        browser = SimpleTextBrowser(**(browser_config))
        browser.page_down()
        header, content = WebSurferService._browser_state(browser)
        return header.strip() + "\n=======================\n" + content

    @staticmethod
    def answer_from_page(
        current_session_id: Annotated[str, "The current session ID."],
        question: Annotated[Optional[str], "[Optional] The question to directly answer. (Defaults to summarizing current page)"] = None,
        url: Annotated[Optional[str], "[Optional] The url of the page. (Defaults to the current page)"] = None,
    ) -> str:
        load_dotenv(find_dotenv(usecwd=True))
        summarizer_llm_config={"model": "gpt-3.5-turbo-1106", "api_key": os.getenv('OPENAI_API_KEY')}
        browser_config={"current_session_id": current_session_id, "downloads_folder": os.getenv('SCRATCH_DIR'), "bing_api_key": os.getenv('BING_API_KEY')}
        browser = SimpleTextBrowser(**(browser_config))
        summarization_client = WebSurferService._create_summarizer_client(summarizer_llm_config)
        if not summarization_client:
            return "Could not create a summarization client!"
        if url is not None and url != browser.address:
            browser.visit_page(url)

        # We are likely going to need to fix this later, but summarize only as many tokens that fit in the buffer
        limit = 4096
        try:
            limit = get_max_token_limit(summarizer_llm_config["model"])  # type: ignore[index]
        except ValueError:
            pass  # limit is unknown
        except TypeError:
            pass  # limit is unknown

        if limit < 16000:
            logger.warning(
                f"The token limit ({limit}) of the WebSurferAgent.summarizer_llm_config, is below the recommended 16k."
            )

        buffer = ""
        for line in re.split(r"([\r\n]+)", browser.page_content):
            tokens = count_token(buffer + line)
            if tokens + 1024 > limit:  # Leave room for our summary
                break
            buffer += line

        buffer = buffer.strip()
        if len(buffer) == 0:
            return "Nothing to summarize."

        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that can summarize long documents to answer question.",
            }
        ]

        prompt = f"Please summarize the following into one or two paragraph:\n\n{buffer}"
        if question is not None:
            prompt = f"Please summarize the following into one or two paragraphs with respect to '{question}':\n\n{buffer}"

        messages.append(
            {"role": "user", "content": prompt},
        )

        response = summarization_client.create(context=None, messages=messages)  # type: ignore[union-attr]
        extracted_response = summarization_client.extract_text_or_completion_object(response)[0]  # type: ignore[union-attr]
        return str(extracted_response)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import asyncio
import json
import os
import logging

from typing import Optional
from urllib.parse import urlparse
from dotenv import load_dotenv

import httplib2
from pydantic import BaseModel, validator
logger = logging.getLogger(__name__)

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    raise ImportError(
        "To use this module, you should have the `google-api-python-client` Python package installed. "
        "You can install it by running the command: `pip install -e.[search-google]`"
    )


class GoogleAPIWrapper(BaseModel):
    google_api_key: Optional[str] = None
    google_cse_id: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

    @validator("google_api_key", always=True)
    @classmethod
    def check_google_api_key(cls, val: str):
        load_dotenv()
        val = val or os.getenv("GOOGLE_API_KEY")
        if not val:
            raise ValueError(
                "To use, make sure you provide the google_api_key when constructing an object. Alternatively, "
                "ensure that the environment variable GOOGLE_API_KEY is set with your API key. You can obtain "
                "an API key from https://console.cloud.google.com/apis/credentials."
            )
        return val

    @validator("google_cse_id", always=True)
    @classmethod
    def check_google_cse_id(cls, val: str):
        load_dotenv()
        val = val or os.getenv("GOOGLE_CSE_ID")
        if not val:
            raise ValueError(
                "To use, make sure you provide the google_cse_id when constructing an object. Alternatively, "
                "ensure that the environment variable GOOGLE_CSE_ID is set with your API key. You can obtain "
                "an API key from https://programmablesearchengine.google.com/controlpanel/create."
            )
        return val

    @property
    def google_api_client(self):
        build_kwargs = {"developerKey": self.google_api_key}
        load_dotenv()
        proxy = os.getenv("GLOBAL_PROXY")
        if proxy:
            parse_result = urlparse(proxy)
            proxy_type = parse_result.scheme
            if proxy_type == "https":
                proxy_type = "http"
            build_kwargs["http"] = httplib2.Http(
                proxy_info=httplib2.ProxyInfo(
                    getattr(httplib2.socks, f"PROXY_TYPE_{proxy_type.upper()}"),
                    parse_result.hostname,
                    parse_result.port,
                ),
            )
        service = build("customsearch", "v1", **build_kwargs)
        return service.cse()

    async def run(
        self,
        query: str,
        max_results: int = 8,
        as_string: bool = True,
        focus: list[str] | None = None,
    ) -> str | list[dict]:
        """Return the results of a Google search using the official Google API.

        Args:
            query: The search query.
            max_results: The number of results to return.
            as_string: A boolean flag to determine the return type of the results. If True, the function will
                return a formatted string with the search results. If False, it will return a list of dictionaries
                containing detailed information about each search result.
            focus: Specific information to be focused on from each search result.

        Returns:
            The results of the search.
        """
        wrapper = GoogleAPIWrapper()
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(
            self.executor, wrapper.google_api_client.list(q=query, num=max_results, cx=wrapper.google_cse_id).execute
        )
        try:
            result = await future
            # Extract the search result items from the response
            search_results = result.get("items", [])

        except HttpError as e:
            # Handle errors in the API call
            logger.exception(f"fail to search {query} for {e}")
            search_results = []

        focus = focus or ["snippet", "link", "title"]
        details = [{i: j for i, j in item_dict.items() if i in focus} for item_dict in search_results]
        # Return the list of search result URLs
        if as_string:
            return safe_google_results(details)

        return details


def safe_google_results(results: str | list) -> str:
    """Return the results of a google search in a safe format.

    Args:
        results: The search results.

    Returns:
        The results of the search.
    """
    if isinstance(results, list):
        safe_message = json.dumps([result for result in results])
    else:
        safe_message = results.encode("utf-8", "ignore").decode("utf-8")
    return safe_message
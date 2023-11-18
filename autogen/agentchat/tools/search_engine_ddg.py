#!/usr/bin/env python

from __future__ import annotations

import asyncio
import json
import os
from concurrent import futures
from typing import Literal, overload
from dotenv import load_dotenv

try:
    from duckduckgo_search import DDGS
except ImportError:
    raise ImportError(
        "To use this module, you should have the `duckduckgo_search` Python package installed. "
        "You can install it by running the command: `pip install -e.[search-ddg]`"
    )

class DDGAPIWrapper:
    """Wrapper around duckduckgo_search API.

    To use this module, you should have the `duckduckgo_search` Python package installed.
    """

    async def run(
        self,
        query: str,
        max_results: int = 8,
        as_string: bool = True,
    ) -> str | list[dict]:
        """Return the results of a Google search using the official Google API

        Args:
            query: The search query.
            max_results: The number of results to return.
            as_string: A boolean flag to determine the return type of the results. If True, the function will
                return a formatted string with the search results. If False, it will return a list of dictionaries
                containing detailed information about each search result.

        Returns:
            The results of the search.
        """
        load_dotenv()
        proxy = os.getenv("GLOBAL_PROXY")
        kwargs = {}
        if proxy:
            kwargs["proxies"] = proxy
        wrapper = DDGAPIWrapper()
        wrapper.ddgs = DDGS(**kwargs)
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(
            None,
            wrapper._search_from_ddgs,
            query,
            max_results,
        )
        search_results = await future

        # Return the list of search result URLs
        if as_string:
            return json.dumps(search_results, ensure_ascii=False)
        return search_results

    def _search_from_ddgs(self, query: str, max_results: int):
        return [
            {"link": i["href"], "snippet": i["body"], "title": i["title"]}
            for (_, i) in zip(range(max_results), self.ddgs.text(query))
        ]
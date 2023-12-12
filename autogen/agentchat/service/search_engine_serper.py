#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/23 18:27
@Author  : alexanderwu
@File    : search_engine_serpapi.py
"""
import json
from typing import Any, Dict, Optional, Tuple, Literal, List

import aiohttp
import os
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv


class WebSearchSerperWrapper(BaseModel):
    payload: dict = Field(default={"page": 1, "num": 10})
    serper_api_key: Optional[str] = None
    aiosession: Optional[aiohttp.ClientSession] = None
    gl: str = "us"
    hl: str = "en"
    type: Literal["news", "search", "places", "images", "videos"] = "search"
    result_key_for_type: Dict = {
        "news": "news",
        "places": "places",
        "images": "images",
        "search": "organic",
        "videos": "videos",
        "shopping": "shopping",
    }
    max_results: Optional[int] = 8

    tbs: Optional[str] = None
    class Config:
        arbitrary_types_allowed = True

    @validator("serper_api_key", always=True)
    @classmethod
    def check_serper_api_key(cls, val: str):
        load_dotenv()
        val = val or os.getenv("SERPER_API_KEY")
        if not val:
            raise ValueError(
                "To use, make sure you provide the serper_api_key when constructing an object. Alternatively, "
                "ensure that the environment variable SERPER_API_KEY is set with your API key. You can obtain "
                "an API key from https://serper.dev/."
            )
        return val

    @staticmethod
    async def run(queries: List[str], max_results: int = 8, type: str = 'search', tbs: str = None, **args) -> str:
        """Run query through Serper and parse result async."""
        wrapper = WebSearchSerperWrapper(type=type, tbs=tbs, max_results=max_results)
        if isinstance(queries, str):
            return wrapper._process_response((await wrapper.results(queries))[0])
        else:
            results = [wrapper._process_response(res) for res in await wrapper.results(queries)]
        return "\n".join(results)

    async def results(self, queries: list[str]) -> dict:
        """Use aiohttp to run query through Serper and return the results async."""

        def construct_url_and_payload_and_headers() -> Tuple[str, Dict[str, str]]:
            payloads = self.get_payloads(queries)
            url = f"https://google.serper.dev/{self.type}"
            headers = self.get_headers()
            return url, payloads, headers

        url, payloads, headers = construct_url_and_payload_and_headers()
        if not self.aiosession:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=payloads, headers=headers) as response:
                    res = await response.json()
        else:
            async with self.aiosession.get.post(url, data=payloads, headers=headers) as response:
                res = await response.json()

        return res

    def get_payloads(self, queries: list[str]) -> Dict[str, str]:
        """Get payloads for Serper."""
        payloads = []
        for query in queries:
            _payload = {
                "q": query,
                "num": self.max_results,
                "gl": self.gl,
                "hl": self.hl
            }
            payloads.append({**self.payload, **_payload})
        return json.dumps(payloads, sort_keys=True)

    def get_headers(self) -> Dict[str, str]:
        headers = {"X-API-KEY": self.serper_api_key, "Content-Type": "application/json"}
        return headers

    def _process_response(self, results: dict) -> str:
        """Process response from SerpAPI."""
        # logger.debug(res)
        focus = ["title", "snippet", "link", "date"]
        def get_focused(x):
            return {i: j for i, j in x.items() if i in focus}
        
        snippets = []
        if results.get("answerBox"):
            answer_box = results.get("answerBox", {})
            if answer_box.get("answer"):
                return answer_box.get("answer")
            elif answer_box.get("snippet"):
                return answer_box.get("snippet").replace("\n", " ")
            elif answer_box.get("snippetHighlighted"):
                return answer_box.get("snippetHighlighted")

        if results.get("knowledgeGraph"):
            kg = results.get("knowledgeGraph", {})
            title = kg.get("title")
            entity_type = kg.get("type")
            if entity_type:
                snippets.append(f"{title}: {entity_type}.")
            description = kg.get("description")
            if description:
                snippets.append(description)
            for attribute, value in kg.get("attributes", {}).items():
                snippets.append(f"{title} {attribute}: {value}.")

        for result in results[self.result_key_for_type[self.type]][:self.max_results]:
            # Handling different types of results
            if self.type == "images":
                if "title" in result:
                    snippets.append(f"Title: {result['title']}")
                if "link" in result:
                    snippets.append(f"Image URL: {result['link']}")
                if "snippet" in result:
                    snippets.append(f"Description: {result['snippet']}")
                snippets.append("---")
            elif self.type == "videos":
                if "title" in result:
                    snippets.append(f"Title: {result['title']}")
                if "link" in result:
                    snippets.append(f"Video URL: {result['link']}")
                if "date" in result:
                    snippets.append(f"Date: {result['date']}")
                if "snippet" in result:
                    snippets.append(f"Description: {result['snippet']}")
                snippets.append("---")
            elif self.type == "places":
                if "title" in result:
                    snippets.append(f"Title: {result['title']}")
                if "address" in result:
                    snippets.append(f"Address: {result['address']}")
                if "latitude" in result and "longitude" in result:
                    snippets.append(f"Location: Latitude {result['latitude']}, Longitude {result['longitude']}")
                if "rating" in result:
                    snippets.append(f"Rating: {result['rating']} ({result.get('ratingCount', 'N/A')} reviews)")
                snippets.append("---")
            elif self.type == "news":
                if "title" in result:
                    snippets.append(f"Title: {result['title']}")
                if "link" in result:
                    snippets.append(f"News URL: {result['link']}")
                if "date" in result:
                    snippets.append(f"Date: {result['date']}")
                if "source" in result:
                    snippets.append(f"Source: {result['source']}")
                snippets.append("---")
            elif self.type == "shopping":
                if "title" in result:
                    snippets.append(f"Title: {result['title']}")
                if "price" in result:
                    snippets.append(f"Price: {result['price']}")
                if "source" in result:
                    snippets.append(f"Source: {result['source']}")
                if "link" in result:
                    snippets.append(f"Product URL: {result['link']}")
                if "delivery" in result:
                    snippets.append(f"Delivery: {result['delivery']}")
                if "rating" in result:
                    snippets.append(f"Rating: {result['rating']} ({result.get('ratingCount', 'N/A')} reviews)")
                if "offers" in result:
                    snippets.append(f"Offers: {result['offers']}")
                if "productId" in result:
                    snippets.append(f"Product ID: {result['productId']}")
                snippets.append("---")

        if results.get("organic"):
            for item in results.get("organic"):
                focused_item = get_focused(item)
                item_str = ", ".join([f"{key}: {value}" for key, value in focused_item.items()])
                snippets.append(item_str)
        
        if len(snippets) == 0:
            return "No good Google Search Result was found"
        
        return "\n".join(snippets)

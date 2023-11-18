#!/usr/bin/env python

from __future__ import annotations
import json
import importlib


class WebBrowserEngine:
    @staticmethod
    async def run(
        url: str, *urls: str
    ):
        module = "autogen.agentchat.tools.web_browser_engine_playwright"
        run_func = importlib.import_module(module).PlaywrightWrapper().run
        return await run_func(url, *urls)

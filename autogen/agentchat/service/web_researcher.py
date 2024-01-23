#!/usr/bin/env python

from autogen.agentchat.contrib.web_surfer import WebSurferAgent
from autogen import UserProxyAgent
from dotenv import load_dotenv
from typing import  Optional
import os
class WebSurf:
    web_surfer:WebSurferAgent = None
    user_proxy:WebSurferAgent = None
    @staticmethod
    async def run(
        query: str,
        clear_history: Optional[bool] = None
    ):
        from . import MakeService
        load_dotenv()
        page_size = 4096
        if not WebSurf.web_surfer:
            WebSurf.web_surfer = WebSurferAgent(
                "web_surfer",
                llm_config={"model": "gpt-4-1106-preview", "api_key": MakeService.auth.api_key},
                summarizer_llm_config={"model": "gpt-3.5-turbo-1106", "api_key": MakeService.auth.api_key},
                browser_config={"viewport_size": page_size, "bing_api_key": os.getenv('BING_API_KEY')},
            )
        if not WebSurf.user_proxy:
            WebSurf.user_proxy = UserProxyAgent(
                "user_proxy",
                human_input_mode="NEVER",
                code_execution_config=False,
                default_auto_reply="",
                is_termination_msg=lambda x: True,
            )

        await WebSurf.user_proxy.a_initiate_chat(WebSurf.web_surfer, clear_history=clear_history or False, message=query)
        return WebSurf.user_proxy.last_message(WebSurf.web_surfer)["content"]
       
            
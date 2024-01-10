#!/usr/bin/env python

from __future__ import annotations

class WebResearcher:
    @staticmethod
    async def run(
        topic: str
    ):
        from . import BackendService, WebResearchInput
        response, err = await BackendService.web_research(WebResearchInput(
            topic=topic
        ))
        if err is not None:
            return err
        return response

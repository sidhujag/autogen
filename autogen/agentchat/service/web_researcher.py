#!/usr/bin/env python

from __future__ import annotations
import re
import sys
import os
# Adjust the path to point to the MetaGPT directory
metagpt_path = os.path.join(os.path.dirname(__file__), "../../../MetaGPT")
sys.path.append(metagpt_path)

from metagpt.roles import researcher

class WebResearcher:
    @staticmethod
    async def run(
        topic: str, **args
    ):
        filename = re.sub(r'[\\/:"*?<>|]+', " ", topic)
        filename = filename.replace("\n", "")
        await researcher.Researcher().run(topic)
        return (researcher.RESEARCH_PATH / f"{filename}.md").read_text()

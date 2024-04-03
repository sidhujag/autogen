"use strict";(self.webpackChunkwebsite=self.webpackChunkwebsite||[]).push([[3400],{48179:(e,n,t)=>{t.r(n),t.d(n,{assets:()=>l,contentTitle:()=>o,default:()=>u,frontMatter:()=>s,metadata:()=>r,toc:()=>c});var i=t(85893),a=t(11151);const s={title:"Agent AutoBuild - Automatically Building Multi-agent Systems",authors:["LinxinS97","jieyuz2"],tags:["LLM","research"]},o=void 0,r={permalink:"/autogen/blog/2023/11/26/Agent-AutoBuild",source:"@site/blog/2023-11-26-Agent-AutoBuild/index.mdx",title:"Agent AutoBuild - Automatically Building Multi-agent Systems",description:"Overall structure of AutoBuild",date:"2023-11-26T00:00:00.000Z",formattedDate:"November 26, 2023",tags:[{label:"LLM",permalink:"/autogen/blog/tags/llm"},{label:"research",permalink:"/autogen/blog/tags/research"}],readingTime:6.815,hasTruncateMarker:!1,authors:[{name:"Linxin Song",title:"MS student at Waseda University",url:"https://linxins97.github.io/",imageURL:"https://github.com/LinxinS97.png",key:"LinxinS97"},{name:"Jieyu Zhang",title:"PhD student at University of Washington",url:"https://jieyuz2.github.io/",imageURL:"https://github.com/jieyuz2.png",key:"jieyuz2"}],frontMatter:{title:"Agent AutoBuild - Automatically Building Multi-agent Systems",authors:["LinxinS97","jieyuz2"],tags:["LLM","research"]},unlisted:!1,prevItem:{title:"AutoGen Studio: Interactively Explore Multi-Agent Workflows",permalink:"/autogen/blog/2023/12/01/AutoGenStudio"},nextItem:{title:"How to Assess Utility of LLM-powered Applications?",permalink:"/autogen/blog/2023/11/20/AgentEval"}},l={authorsImageUrls:[void 0,void 0]},c=[{value:"Introduction",id:"introduction",level:2},{value:"Installation",id:"installation",level:2},{value:"Basic Example",id:"basic-example",level:2},{value:"Step 1: prepare configurations",id:"step-1-prepare-configurations",level:3},{value:"Step 2: create an AgentBuilder instance",id:"step-2-create-an-agentbuilder-instance",level:3},{value:"Step 3: specify the building task",id:"step-3-specify-the-building-task",level:3},{value:"Step 4: build group chat agents",id:"step-4-build-group-chat-agents",level:3},{value:"Step 5: execute the task",id:"step-5-execute-the-task",level:3},{value:"Step 6 (Optional): clear all agents and prepare for the next task",id:"step-6-optional-clear-all-agents-and-prepare-for-the-next-task",level:3},{value:"Save and Load",id:"save-and-load",level:2},{value:"Use OpenAI Assistant",id:"use-openai-assistant",level:2},{value:"(Experimental) Use Open-source LLM",id:"experimental-use-open-source-llm",level:2},{value:"Future work/Roadmap",id:"future-workroadmap",level:2},{value:"Summary",id:"summary",level:2}];function d(e){const n={a:"a",code:"code",h2:"h2",h3:"h3",img:"img",li:"li",p:"p",pre:"pre",strong:"strong",ul:"ul",...(0,a.a)(),...e.components};return(0,i.jsxs)(i.Fragment,{children:[(0,i.jsx)(n.p,{children:(0,i.jsx)(n.img,{alt:"Overall structure of AutoBuild",src:t(50623).Z+"",width:"2641",height:"1738"})}),"\n",(0,i.jsxs)(n.p,{children:[(0,i.jsx)(n.strong,{children:"TL;DR:"}),"\nIntroducing ",(0,i.jsx)(n.strong,{children:"AutoBuild"}),", building multi-agent system automatically, fast, and easily for complex tasks with minimal\nuser prompt required, powered by a new designed class ",(0,i.jsx)(n.strong,{children:"AgentBuilder"}),". AgentBuilder also supports open-source LLMs by\nleveraging ",(0,i.jsx)(n.a,{href:"https://docs.vllm.ai/en/latest/index.html",children:"vLLM"})," and ",(0,i.jsx)(n.a,{href:"https://github.com/lm-sys/FastChat",children:"FastChat"}),".\nCheckout example notebooks and source code for reference:"]}),"\n",(0,i.jsxs)(n.ul,{children:["\n",(0,i.jsx)(n.li,{children:(0,i.jsx)(n.a,{href:"https://github.com/microsoft/autogen/blob/main/notebook/autobuild_basic.ipynb",children:"AutoBuild Examples"})}),"\n",(0,i.jsx)(n.li,{children:(0,i.jsx)(n.a,{href:"https://github.com/microsoft/autogen/blob/main/autogen/agentchat/contrib/agent_builder.py",children:"AgentBuilder"})}),"\n"]}),"\n",(0,i.jsx)(n.h2,{id:"introduction",children:"Introduction"}),"\n",(0,i.jsxs)(n.p,{children:["In this blog, we introduce ",(0,i.jsx)(n.strong,{children:"AutoBuild"}),", a pipeline that can automatically build multi-agent systems for complex tasks.\nSpecifically, we design a new class called ",(0,i.jsx)(n.strong,{children:"AgentBuilder"}),", which will complete the generation of participant expert agents\nand the construction of group chat automatically after the user provides descriptions of a building task and an execution task."]}),"\n",(0,i.jsxs)(n.p,{children:["AgentBuilder supports open-source models on Hugging Face powered by ",(0,i.jsx)(n.a,{href:"https://docs.vllm.ai/en/latest/index.html",children:"vLLM"}),"\nand ",(0,i.jsx)(n.a,{href:"https://github.com/lm-sys/FastChat",children:"FastChat"}),". Once the user chooses to use open-source LLM, AgentBuilder will set\nup an endpoint server automatically without any user participation."]}),"\n",(0,i.jsx)(n.h2,{id:"installation",children:"Installation"}),"\n",(0,i.jsxs)(n.ul,{children:["\n",(0,i.jsx)(n.li,{children:"AutoGen:"}),"\n"]}),"\n",(0,i.jsx)(n.pre,{children:(0,i.jsx)(n.code,{className:"language-bash",children:"pip install pyautogen[autobuild]\n"})}),"\n",(0,i.jsxs)(n.ul,{children:["\n",(0,i.jsx)(n.li,{children:"(Optional: if you want to use open-source LLMs) vLLM and FastChat"}),"\n"]}),"\n",(0,i.jsx)(n.pre,{children:(0,i.jsx)(n.code,{className:"language-bash",children:"pip install vllm fastchat\n"})}),"\n",(0,i.jsx)(n.h2,{id:"basic-example",children:"Basic Example"}),"\n",(0,i.jsx)(n.p,{children:"In this section, we provide a step-by-step example of how to use AgentBuilder to build a multi-agent system for a specific task."}),"\n",(0,i.jsx)(n.h3,{id:"step-1-prepare-configurations",children:"Step 1: prepare configurations"}),"\n",(0,i.jsx)(n.p,{children:"First, we need to prepare the Agent configurations.\nSpecifically, a config path containing the model name and API key, and a default config for each agent, are required."}),"\n",(0,i.jsx)(n.pre,{children:(0,i.jsx)(n.code,{className:"language-python",children:"config_file_or_env = '/home/elpis_ubuntu/LLM/autogen/OAI_CONFIG_LIST'  # modify path\ndefault_llm_config = {\n    'temperature': 0\n}\n"})}),"\n",(0,i.jsx)(n.h3,{id:"step-2-create-an-agentbuilder-instance",children:"Step 2: create an AgentBuilder instance"}),"\n",(0,i.jsx)(n.p,{children:"Then, we create an AgentBuilder instance with the config path and default config.\nYou can also specific the builder model and agent model, which are the LLMs used for building and agent respectively."}),"\n",(0,i.jsx)(n.pre,{children:(0,i.jsx)(n.code,{className:"language-python",children:"from autogen.agentchat.contrib.agent_builder import AgentBuilder\n\nbuilder = AgentBuilder(config_file_or_env=config_file_or_env, builder_model='gpt-4-turbo-preview', agent_model='gpt-4-turbo-preview')\n"})}),"\n",(0,i.jsx)(n.h3,{id:"step-3-specify-the-building-task",children:"Step 3: specify the building task"}),"\n",(0,i.jsx)(n.p,{children:"Specify a building task with a general description. Building task will help the build manager (a LLM) decide what agents should be built.\nNote that your building task should have a general description of the task. Adding some specific examples is better."}),"\n",(0,i.jsx)(n.pre,{children:(0,i.jsx)(n.code,{className:"language-python",children:'building_task = "Find a paper on arxiv by programming, and analyze its application in some domain. For example, find a latest paper about gpt-4 on arxiv and find its potential applications in software."\n'})}),"\n",(0,i.jsx)(n.h3,{id:"step-4-build-group-chat-agents",children:"Step 4: build group chat agents"}),"\n",(0,i.jsxs)(n.p,{children:["Use ",(0,i.jsx)(n.code,{children:"build()"})," to let the build manager (with a ",(0,i.jsx)(n.code,{children:"builder_model"})," as backbone) complete the group chat agents generation.\nIf you think coding is necessary for your task, you can use ",(0,i.jsx)(n.code,{children:"coding=True"})," to add a user proxy (a local code interpreter) into the agent list as:"]}),"\n",(0,i.jsx)(n.pre,{children:(0,i.jsx)(n.code,{className:"language-python",children:"agent_list, agent_configs = builder.build(building_task, default_llm_config, coding=True)\n"})}),"\n",(0,i.jsxs)(n.p,{children:["If ",(0,i.jsx)(n.code,{children:"coding"})," is not specified, AgentBuilder will determine on its own whether the user proxy should be added or not according to the task.\nThe generated ",(0,i.jsx)(n.code,{children:"agent_list"})," is a list of ",(0,i.jsx)(n.code,{children:"AssistantAgent"})," instances.\nIf ",(0,i.jsx)(n.code,{children:"coding"})," is true, a user proxy (a ",(0,i.jsx)(n.code,{children:"UserProxyAssistant"})," instance) will be added as the first element to the ",(0,i.jsx)(n.code,{children:"agent_list"}),".\n",(0,i.jsx)(n.code,{children:"agent_configs"})," is a list of agent configurations including agent name, backbone LLM model, and system message.\nFor example"]}),"\n",(0,i.jsx)(n.pre,{children:(0,i.jsx)(n.code,{children:'// an example of agent_configs. AgentBuilder will generate agents with the following configurations.\n[\n    {\n        "name": "ArXiv_Data_Scraper_Developer",\n        "model": "gpt-4-turbo-preview",\n        "system_message": "You are now in a group chat. You need to complete a task with other participants. As an ArXiv_Data_Scraper_Developer, your focus is to create and refine tools capable of intelligent search and data extraction from arXiv, honing in on topics within the realms of computer science and medical science. Utilize your proficiency in Python programming to design scripts that navigate, query, and parse information from the platform, generating valuable insights and datasets for analysis. \\n\\nDuring your mission, it\\u2019s not just about formulating queries; your role encompasses the optimization and precision of the data retrieval process, ensuring relevance and accuracy of the information extracted. If you encounter an issue with a script or a discrepancy in the expected output, you are encouraged to troubleshoot and offer revisions to the code you find in the group chat.\\n\\nWhen you reach a point where the existing codebase does not fulfill task requirements or if the operation of provided code is unclear, you should ask for help from the group chat manager. They will facilitate your advancement by providing guidance or appointing another participant to assist you. Your ability to adapt and enhance scripts based on peer feedback is critical, as the dynamic nature of data scraping demands ongoing refinement of techniques and approaches.\\n\\nWrap up your participation by confirming the user\'s need has been satisfied with the data scraping solutions you\'ve provided. Indicate the completion of your task by replying \\"TERMINATE\\" in the group chat.",\n        "description": "ArXiv_Data_Scraper_Developer is a specialized software development role requiring proficiency in Python, including familiarity with web scraping libraries such as BeautifulSoup or Scrapy, and a solid understanding of APIs and data parsing. They must possess the ability to identify and correct errors in existing scripts and confidently engage in technical discussions to improve data retrieval processes. The role also involves a critical eye for troubleshooting and optimizing code to ensure efficient data extraction from the ArXiv platform for research and analysis purposes."\n    },\n    ...\n]\n'})}),"\n",(0,i.jsx)(n.h3,{id:"step-5-execute-the-task",children:"Step 5: execute the task"}),"\n",(0,i.jsxs)(n.p,{children:["Let agents generated in ",(0,i.jsx)(n.code,{children:"build()"})," complete the task collaboratively in a group chat."]}),"\n",(0,i.jsx)(n.pre,{children:(0,i.jsx)(n.code,{className:"language-python",children:'import autogen\n\ndef start_task(execution_task: str, agent_list: list, llm_config: dict):\n    config_list = autogen.config_list_from_json(config_file_or_env, filter_dict={"model": ["gpt-4-turbo-preview"]})\n\n    group_chat = autogen.GroupChat(agents=agent_list, messages=[], max_round=12)\n    manager = autogen.GroupChatManager(\n        groupchat=group_chat, llm_config={"config_list": config_list, **llm_config}\n    )\n    agent_list[0].initiate_chat(manager, message=execution_task)\n\nstart_task(\n    execution_task="Find a recent paper about gpt-4 on arxiv and find its potential applications in software.",\n    agent_list=agent_list,\n    llm_config=default_llm_config\n)\n'})}),"\n",(0,i.jsx)(n.h3,{id:"step-6-optional-clear-all-agents-and-prepare-for-the-next-task",children:"Step 6 (Optional): clear all agents and prepare for the next task"}),"\n",(0,i.jsx)(n.p,{children:"You can clear all agents generated in this task by the following code if your task is completed or if the next task is largely different from the current task."}),"\n",(0,i.jsx)(n.pre,{children:(0,i.jsx)(n.code,{className:"language-python",children:"builder.clear_all_agents(recycle_endpoint=True)\n"})}),"\n",(0,i.jsxs)(n.p,{children:["If the agent's backbone is an open-source LLM, this process will also shut down the endpoint server. More details are in the next section.\nIf necessary, you can use ",(0,i.jsx)(n.code,{children:"recycle_endpoint=False"})," to retain the previous open-source LLM's endpoint server."]}),"\n",(0,i.jsx)(n.h2,{id:"save-and-load",children:"Save and Load"}),"\n",(0,i.jsx)(n.p,{children:"You can save all necessary information of the built group chat agents by"}),"\n",(0,i.jsx)(n.pre,{children:(0,i.jsx)(n.code,{className:"language-python",children:"saved_path = builder.save()\n"})}),"\n",(0,i.jsx)(n.p,{children:"Configurations will be saved in JSON format with the following content:"}),"\n",(0,i.jsx)(n.pre,{children:(0,i.jsx)(n.code,{className:"language-json",children:'// FILENAME: save_config_TASK_MD5.json\n{\n    "building_task": "Find a paper on arxiv by programming, and analysis its application in some domain. For example, find a latest paper about gpt-4 on arxiv and find its potential applications in software.",\n    "agent_configs": [\n        {\n            "name": "...",\n            "model": "...",\n            "system_message": "...",\n            "description": "..."\n        },\n        ...\n    ],\n    "manager_system_message": "...",\n    "code_execution_config": {...},\n    "default_llm_config": {...}\n}\n'})}),"\n",(0,i.jsxs)(n.p,{children:["You can provide a specific filename, otherwise, AgentBuilder will save config to the current path with the generated filename ",(0,i.jsx)(n.code,{children:"save_config_TASK_MD5.json"}),"."]}),"\n",(0,i.jsx)(n.p,{children:"You can load the saved config and skip the building process. AgentBuilder will create agents with those information without prompting the build manager."}),"\n",(0,i.jsx)(n.pre,{children:(0,i.jsx)(n.code,{className:"language-python",children:"new_builder = AgentBuilder(config_file_or_env=config_file_or_env)\nagent_list, agent_config = new_builder.load(saved_path)\nstart_task(...)  # skip build()\n"})}),"\n",(0,i.jsx)(n.h2,{id:"use-openai-assistant",children:"Use OpenAI Assistant"}),"\n",(0,i.jsxs)(n.p,{children:[(0,i.jsx)(n.a,{href:"https://platform.openai.com/docs/assistants/overview",children:"Assistants API"})," allows you to build AI assistants within your own applications.\nAn Assistant has instructions and can leverage models, tools, and knowledge to respond to user queries.\nAutoBuild also supports the assistant API by adding ",(0,i.jsx)(n.code,{children:"use_oai_assistant=True"})," to ",(0,i.jsx)(n.code,{children:"build()"}),"."]}),"\n",(0,i.jsx)(n.pre,{children:(0,i.jsx)(n.code,{className:"language-python",children:"# Transfer to the OpenAI Assistant API.\nagent_list, agent_config = new_builder.build(building_task, default_llm_config, use_oai_assistant=True)\n...\n"})}),"\n",(0,i.jsx)(n.h2,{id:"experimental-use-open-source-llm",children:"(Experimental) Use Open-source LLM"}),"\n",(0,i.jsxs)(n.p,{children:["AutoBuild supports open-source LLM by ",(0,i.jsx)(n.a,{href:"https://docs.vllm.ai/en/latest/index.html",children:"vLLM"})," and ",(0,i.jsx)(n.a,{href:"https://github.com/lm-sys/FastChat",children:"FastChat"}),".\nCheck the supported model list ",(0,i.jsx)(n.a,{href:"https://docs.vllm.ai/en/latest/models/supported_models.html",children:"here"}),".\nAfter satisfying the requirements, you can add an open-source LLM's huggingface repository to the config file,"]}),"\n",(0,i.jsx)(n.pre,{children:(0,i.jsx)(n.code,{className:"language-json,",children:'// Add the LLM\'s huggingface repo to your config file and use EMPTY as the api_key.\n[\n    ...\n    {\n        "model": "meta-llama/Llama-2-13b-chat-hf",\n        "api_key": "EMPTY"\n    }\n]\n'})}),"\n",(0,i.jsx)(n.p,{children:"and specify it when initializing AgentBuilder.\nAgentBuilder will automatically set up an endpoint server for open-source LLM. Make sure you have sufficient GPUs resources."}),"\n",(0,i.jsx)(n.h2,{id:"future-workroadmap",children:"Future work/Roadmap"}),"\n",(0,i.jsxs)(n.ul,{children:["\n",(0,i.jsx)(n.li,{children:"Let the builder select the best agents from a given library/database to solve the task."}),"\n"]}),"\n",(0,i.jsx)(n.h2,{id:"summary",children:"Summary"}),"\n",(0,i.jsxs)(n.p,{children:["We propose AutoBuild with a new class ",(0,i.jsx)(n.code,{children:"AgentBuilder"}),".\nAutoBuild can help user solve their complex task with an automatically built multi-agent system.\nAutoBuild supports open-source LLMs and GPTs API, giving users more flexibility to choose their favorite models.\nMore advanced features are coming soon."]})]})}function u(e={}){const{wrapper:n}={...(0,a.a)(),...e.components};return n?(0,i.jsx)(n,{...e,children:(0,i.jsx)(d,{...e})}):d(e)}},50623:(e,n,t)=>{t.d(n,{Z:()=>i});const i=t.p+"assets/images/agent_autobuild-e48543a81e85bb185c7365db1290a91a.png"},11151:(e,n,t)=>{t.d(n,{Z:()=>r,a:()=>o});var i=t(67294);const a={},s=i.createContext(a);function o(e){const n=i.useContext(s);return i.useMemo((function(){return"function"==typeof e?e(n):{...n,...e}}),[n,e])}function r(e){let n;return n=e.disableParentContext?"function"==typeof e.components?e.components(a):e.components||a:o(e.components),i.createElement(s.Provider,{value:n},e.children)}}}]);
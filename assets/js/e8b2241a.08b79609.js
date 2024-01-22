"use strict";(self.webpackChunkwebsite=self.webpackChunkwebsite||[]).push([[6709],{3905:(e,t,n)=>{n.d(t,{Zo:()=>s,kt:()=>g});var a=n(7294);function l(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function i(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);t&&(a=a.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,a)}return n}function r(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?i(Object(n),!0).forEach((function(t){l(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):i(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function o(e,t){if(null==e)return{};var n,a,l=function(e,t){if(null==e)return{};var n,a,l={},i=Object.keys(e);for(a=0;a<i.length;a++)n=i[a],t.indexOf(n)>=0||(l[n]=e[n]);return l}(e,t);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(e);for(a=0;a<i.length;a++)n=i[a],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(l[n]=e[n])}return l}var c=a.createContext({}),p=function(e){var t=a.useContext(c),n=t;return e&&(n="function"==typeof e?e(t):r(r({},t),e)),n},s=function(e){var t=p(e.components);return a.createElement(c.Provider,{value:t},e.children)},u={inlineCode:"code",wrapper:function(e){var t=e.children;return a.createElement(a.Fragment,{},t)}},d=a.forwardRef((function(e,t){var n=e.components,l=e.mdxType,i=e.originalType,c=e.parentName,s=o(e,["components","mdxType","originalType","parentName"]),d=p(n),g=l,m=d["".concat(c,".").concat(g)]||d[g]||u[g]||i;return n?a.createElement(m,r(r({ref:t},s),{},{components:n})):a.createElement(m,r({ref:t},s))}));function g(e,t){var n=arguments,l=t&&t.mdxType;if("string"==typeof e||l){var i=n.length,r=new Array(i);r[0]=d;var o={};for(var c in t)hasOwnProperty.call(t,c)&&(o[c]=t[c]);o.originalType=e,o.mdxType="string"==typeof e?e:l,r[1]=o;for(var p=2;p<i;p++)r[p]=n[p];return a.createElement.apply(null,r)}return a.createElement.apply(null,n)}d.displayName="MDXCreateElement"},129:(e,t,n)=>{n.r(t),n.d(t,{contentTitle:()=>r,default:()=>s,frontMatter:()=>i,metadata:()=>o,toc:()=>c});var a=n(3117),l=(n(7294),n(3905));const i={sidebar_label:"agent_builder",title:"agentchat.contrib.agent_builder"},r=void 0,o={unversionedId:"reference/agentchat/contrib/agent_builder",id:"reference/agentchat/contrib/agent_builder",isDocsHomePage:!1,title:"agentchat.contrib.agent_builder",description:"AgentBuilder Objects",source:"@site/docs/reference/agentchat/contrib/agent_builder.md",sourceDirName:"reference/agentchat/contrib",slug:"/reference/agentchat/contrib/agent_builder",permalink:"/autogen/docs/reference/agentchat/contrib/agent_builder",editUrl:"https://github.com/microsoft/autogen/edit/main/website/docs/reference/agentchat/contrib/agent_builder.md",tags:[],version:"current",frontMatter:{sidebar_label:"agent_builder",title:"agentchat.contrib.agent_builder"},sidebar:"referenceSideBar",next:{title:"compressible_agent",permalink:"/autogen/docs/reference/agentchat/contrib/compressible_agent"}},c=[{value:"AgentBuilder Objects",id:"agentbuilder-objects",children:[{value:"max_agents",id:"max_agents",children:[],level:4},{value:"__init__",id:"__init__",children:[],level:4},{value:"clear_agent",id:"clear_agent",children:[],level:4},{value:"clear_all_agents",id:"clear_all_agents",children:[],level:4},{value:"build",id:"build",children:[],level:4},{value:"save",id:"save",children:[],level:4},{value:"load",id:"load",children:[],level:4}],level:2}],p={toc:c};function s(e){let{components:t,...n}=e;return(0,l.kt)("wrapper",(0,a.Z)({},p,n,{components:t,mdxType:"MDXLayout"}),(0,l.kt)("h2",{id:"agentbuilder-objects"},"AgentBuilder Objects"),(0,l.kt)("pre",null,(0,l.kt)("code",{parentName:"pre",className:"language-python"},"class AgentBuilder()\n")),(0,l.kt)("p",null,"AgentBuilder can help user build an automatic task solving process powered by multi-agent system.\nSpecifically, our building pipeline includes initialize and build.\nIn build(), we prompt a gpt-4 model to create multiple participant agents, and specify whether\nthis task need programming to solve.\nUser can save the built agents' config by calling save(), and load the saved configs by load(), which can skip the\nbuilding process."),(0,l.kt)("h4",{id:"max_agents"},"max","_","agents"),(0,l.kt)("p",null,"maximum number of agents build manager can create."),(0,l.kt)("h4",{id:"__init__"},"_","_","init","_","_"),(0,l.kt)("pre",null,(0,l.kt)("code",{parentName:"pre",className:"language-python"},'def __init__(config_path: Optional[str] = "OAI_CONFIG_LIST",\n             builder_model: Optional[str] = "gpt-4",\n             agent_model: Optional[str] = "gpt-4",\n             host: Optional[str] = "localhost",\n             endpoint_building_timeout: Optional[int] = 600)\n')),(0,l.kt)("p",null,(0,l.kt)("strong",{parentName:"p"},"Arguments"),":"),(0,l.kt)("ul",null,(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"config_path")," - path of the OpenAI api configs."),(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"builder_model")," - specify a model as the backbone of build manager."),(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"agent_model")," - specify a model as the backbone of participant agents."),(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"host")," - endpoint host."),(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"endpoint_building_timeout")," - timeout for building up an endpoint server.")),(0,l.kt)("h4",{id:"clear_agent"},"clear","_","agent"),(0,l.kt)("pre",null,(0,l.kt)("code",{parentName:"pre",className:"language-python"},"def clear_agent(agent_name: str, recycle_endpoint: Optional[bool] = True)\n")),(0,l.kt)("p",null,"Clear a specific agent by name."),(0,l.kt)("p",null,(0,l.kt)("strong",{parentName:"p"},"Arguments"),":"),(0,l.kt)("ul",null,(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"agent_name")," - the name of agent."),(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"recycle_endpoint")," - trigger for recycle the endpoint server. If true, the endpoint will be recycled\nwhen there is no agent depending on.")),(0,l.kt)("h4",{id:"clear_all_agents"},"clear","_","all","_","agents"),(0,l.kt)("pre",null,(0,l.kt)("code",{parentName:"pre",className:"language-python"},"def clear_all_agents(recycle_endpoint: Optional[bool] = True)\n")),(0,l.kt)("p",null,"Clear all cached agents."),(0,l.kt)("h4",{id:"build"},"build"),(0,l.kt)("pre",null,(0,l.kt)("code",{parentName:"pre",className:"language-python"},"def build(building_task: Optional[str] = None,\n          default_llm_config: Optional[Dict] = None,\n          coding: Optional[bool] = None,\n          cached_configs: Optional[Dict] = None,\n          use_oai_assistant: Optional[bool] = False,\n          code_execution_config: Optional[Dict] = None,\n          **kwargs)\n")),(0,l.kt)("p",null,"Auto build agents based on the building task."),(0,l.kt)("p",null,(0,l.kt)("strong",{parentName:"p"},"Arguments"),":"),(0,l.kt)("ul",null,(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"building_task")," - instruction that helps build manager (gpt-4) to decide what agent should be built."),(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"default_llm_config")," - specific configs for LLM (e.g., config_list, seed, temperature, ...)."),(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"coding")," - use to identify if the user proxy (a code interpreter) should be added."),(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"cached_configs")," - previously saved agent configs."),(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"use_oai_assistant")," - use OpenAI assistant api instead of self-constructed agent."),(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"code_execution_config")," - specific configs for user proxy (e.g., last_n_messages, work_dir, ...).")),(0,l.kt)("h4",{id:"save"},"save"),(0,l.kt)("pre",null,(0,l.kt)("code",{parentName:"pre",className:"language-python"},"def save(filepath: Optional[str] = None) -> str\n")),(0,l.kt)("p",null,"Save building configs. If the filepath is not specific, this function will create a filename by encrypt the\nbuilding",(0,l.kt)("em",{parentName:"p"},'task string by md5 with "save_config'),'" prefix, and save config to the local path.'),(0,l.kt)("p",null,(0,l.kt)("strong",{parentName:"p"},"Arguments"),":"),(0,l.kt)("ul",null,(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"filepath")," - save path.")),(0,l.kt)("p",null,(0,l.kt)("strong",{parentName:"p"},"Returns"),":"),(0,l.kt)("ul",null,(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"filepath")," - path save.")),(0,l.kt)("h4",{id:"load"},"load"),(0,l.kt)("pre",null,(0,l.kt)("code",{parentName:"pre",className:"language-python"},"def load(filepath: Optional[str] = None,\n         config_json: Optional[str] = None,\n         **kwargs)\n")),(0,l.kt)("p",null,"Load building configs and call the build function to complete building without calling online LLMs' api."),(0,l.kt)("p",null,(0,l.kt)("strong",{parentName:"p"},"Arguments"),":"),(0,l.kt)("ul",null,(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"filepath")," - filepath or JSON string for the save config."),(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"config_json")," - JSON string for the save config.")))}s.isMDXComponent=!0}}]);
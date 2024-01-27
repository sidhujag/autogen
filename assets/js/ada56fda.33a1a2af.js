"use strict";(self.webpackChunkwebsite=self.webpackChunkwebsite||[]).push([[9946],{1809:(e,n,o)=>{o.r(n),o.d(n,{assets:()=>s,contentTitle:()=>r,default:()=>u,frontMatter:()=>c,metadata:()=>a,toc:()=>l});var t=o(5893),i=o(1151);const c={title:"Code execution is now by default inside docker container",authors:["olgavrou"],tags:["AutoGen"]},r=void 0,a={permalink:"/autogen/blog/2024/01/23/Code-execution-in-docker",source:"@site/blog/2024-01-23-Code-execution-in-docker/index.mdx",title:"Code execution is now by default inside docker container",description:"TLDR",date:"2024-01-23T00:00:00.000Z",formattedDate:"January 23, 2024",tags:[{label:"AutoGen",permalink:"/autogen/blog/tags/auto-gen"}],readingTime:2.38,hasTruncateMarker:!1,authors:[{name:"Olga Vrousgou",title:"Senior Software Engineer at Microsoft Research",url:"https://github.com/olgavrou/",imageURL:"https://github.com/olgavrou.png",key:"olgavrou"}],frontMatter:{title:"Code execution is now by default inside docker container",authors:["olgavrou"],tags:["AutoGen"]},unlisted:!1,prevItem:{title:"AutoGenBench -- A Tool for Measuring and Evaluating AutoGen Agents",permalink:"/autogen/blog/2024/01/25/AutoGenBench"},nextItem:{title:"All About Agent Descriptions",permalink:"/autogen/blog/2023/12/29/AgentDescriptions"}},s={authorsImageUrls:[void 0]},l=[{value:"TLDR",id:"tldr",level:2},{value:"Introduction",id:"introduction",level:2},{value:"Example",id:"example",level:2},{value:"Diasable code execution entirely",id:"diasable-code-execution-entirely",level:3},{value:"Run code execution locally",id:"run-code-execution-locally",level:3},{value:"Related documentation",id:"related-documentation",level:2},{value:"Conclusion",id:"conclusion",level:2}];function d(e){const n={a:"a",code:"code",h2:"h2",h3:"h3",li:"li",p:"p",pre:"pre",ul:"ul",...(0,i.a)(),...e.components};return(0,t.jsxs)(t.Fragment,{children:[(0,t.jsx)(n.h2,{id:"tldr",children:"TLDR"}),"\n",(0,t.jsx)(n.p,{children:"AutoGen 0.2.8 enhances operational safety by making 'code execution inside a Docker container' the default setting, focusing on informing users about its operations and empowering them to make informed decisions regarding code execution."}),"\n",(0,t.jsxs)(n.p,{children:["The new release introduces a breaking change where the ",(0,t.jsx)(n.code,{children:"use_docker"})," argument is set to ",(0,t.jsx)(n.code,{children:"True"})," by default in code executing agents. This change underscores our commitment to prioritizing security and safety in AutoGen."]}),"\n",(0,t.jsx)(n.h2,{id:"introduction",children:"Introduction"}),"\n",(0,t.jsxs)(n.p,{children:["AutoGen has code-executing agents, usually defined as a ",(0,t.jsx)(n.code,{children:"UserProxyAgent"}),", where code execution is by default ON. Until now, unless explicitly specified by the user, any code generated by other agents would be executed by code-execution agents locally, i.e. wherever AutoGen was being executed. If AutoGen happened to be run in a docker container then the risks of running code were minimized. However, if AutoGen runs outside of Docker, it's easy particularly for new users to overlook code-execution risks."]}),"\n",(0,t.jsx)(n.p,{children:"AutoGen has now changed to by default execute any code inside a docker container (unless execution is already happening inside a docker container). It will launch a Docker image (either user-provided or default), execute the new code, and then terminate the image, preparing for the next code execution cycle."}),"\n",(0,t.jsx)(n.p,{children:"We understand that not everyone is concerned about this especially when playing around with AutoGen for the first time. We have provided easy ways to turn this requirement off. But we believe that making sure that the user is aware of the fact that code will be executed locally, and prompting them to think about the security implications of running code locally is the right step for AutoGen."}),"\n",(0,t.jsx)(n.h2,{id:"example",children:"Example"}),"\n",(0,t.jsx)(n.p,{children:"The example shows the default behaviour which is that any code generated by assistant agent and executed by user_proxy agent, will attempt to use a docker container to execute the code. If docker is not running, it will throw an error. User can decide to activate docker or opt in for local code execution."}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-python",children:'from autogen import AssistantAgent, UserProxyAgent, config_list_from_json\nassistant = AssistantAgent("assistant", llm_config={"config_list": config_list})\nuser_proxy = UserProxyAgent("user_proxy", code_execution_config={"work_dir": "coding"})\nuser_proxy.initiate_chat(assistant, message="Plot a chart of NVDA and TESLA stock price change YTD.")\n'})}),"\n",(0,t.jsx)(n.p,{children:"To opt out of from this default behaviour there are some options."}),"\n",(0,t.jsx)(n.h3,{id:"diasable-code-execution-entirely",children:"Diasable code execution entirely"}),"\n",(0,t.jsxs)(n.ul,{children:["\n",(0,t.jsxs)(n.li,{children:["Set ",(0,t.jsx)(n.code,{children:"code_execution_config"})," to ",(0,t.jsx)(n.code,{children:"False"})," for each code-execution agent. E.g.:"]}),"\n"]}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-python",children:'user_proxy = autogen.UserProxyAgent(name="user_proxy", llm_config=llm_config, code_execution_config=False)\n'})}),"\n",(0,t.jsx)(n.h3,{id:"run-code-execution-locally",children:"Run code execution locally"}),"\n",(0,t.jsxs)(n.ul,{children:["\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.code,{children:"use_docker"})," can be set to ",(0,t.jsx)(n.code,{children:"False"})," in ",(0,t.jsx)(n.code,{children:"code_execution_config"})," for each code-execution agent."]}),"\n",(0,t.jsxs)(n.li,{children:["To set it for all code-execution agents at once: set ",(0,t.jsx)(n.code,{children:"AUTOGEN_USE_DOCKER"})," to ",(0,t.jsx)(n.code,{children:"False"})," as an environment variable."]}),"\n"]}),"\n",(0,t.jsx)(n.p,{children:"E.g.:"}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-python",children:'user_proxy = autogen.UserProxyAgent(name="user_proxy", llm_config=llm_config,\n    code_execution_config={"work_dir":"coding", "use_docker":False})\n'})}),"\n",(0,t.jsx)(n.h2,{id:"related-documentation",children:"Related documentation"}),"\n",(0,t.jsxs)(n.ul,{children:["\n",(0,t.jsx)(n.li,{children:(0,t.jsx)(n.a,{href:"https://microsoft.github.io/autogen/docs/Installation#code-execution-with-docker-default",children:"Code execution with docker"})}),"\n",(0,t.jsx)(n.li,{children:(0,t.jsx)(n.a,{href:"https://microsoft.github.io/autogen/docs/FAQ#agents-are-throwing-due-to-docker-not-running-how-can-i-resolve-this",children:"How to disable code execution in docker"})}),"\n"]}),"\n",(0,t.jsx)(n.h2,{id:"conclusion",children:"Conclusion"}),"\n",(0,t.jsx)(n.p,{children:"AutoGen 0.2.8 now improves the code execution safety and is ensuring that the user is properly informed of what autogen is doing and can make decisions around code-execution."})]})}function u(e={}){const{wrapper:n}={...(0,i.a)(),...e.components};return n?(0,t.jsx)(n,{...e,children:(0,t.jsx)(d,{...e})}):d(e)}},1151:(e,n,o)=>{o.d(n,{Z:()=>a,a:()=>r});var t=o(7294);const i={},c=t.createContext(i);function r(e){const n=t.useContext(c);return t.useMemo((function(){return"function"==typeof e?e(n):{...n,...e}}),[n,e])}function a(e){let n;return n=e.disableParentContext?"function"==typeof e.components?e.components(i):e.components||i:r(e.components),t.createElement(c.Provider,{value:n},e.children)}}}]);
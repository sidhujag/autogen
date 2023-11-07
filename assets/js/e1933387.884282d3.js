"use strict";(self.webpackChunkwebsite=self.webpackChunkwebsite||[]).push([[751],{3905:(e,t,n)=>{n.d(t,{Zo:()=>p,kt:()=>u});var a=n(7294);function r(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function l(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);t&&(a=a.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,a)}return n}function i(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?l(Object(n),!0).forEach((function(t){r(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):l(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function s(e,t){if(null==e)return{};var n,a,r=function(e,t){if(null==e)return{};var n,a,r={},l=Object.keys(e);for(a=0;a<l.length;a++)n=l[a],t.indexOf(n)>=0||(r[n]=e[n]);return r}(e,t);if(Object.getOwnPropertySymbols){var l=Object.getOwnPropertySymbols(e);for(a=0;a<l.length;a++)n=l[a],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(r[n]=e[n])}return r}var o=a.createContext({}),c=function(e){var t=a.useContext(o),n=t;return e&&(n="function"==typeof e?e(t):i(i({},t),e)),n},p=function(e){var t=c(e.components);return a.createElement(o.Provider,{value:t},e.children)},d={inlineCode:"code",wrapper:function(e){var t=e.children;return a.createElement(a.Fragment,{},t)}},g=a.forwardRef((function(e,t){var n=e.components,r=e.mdxType,l=e.originalType,o=e.parentName,p=s(e,["components","mdxType","originalType","parentName"]),g=c(n),u=r,m=g["".concat(o,".").concat(u)]||g[u]||d[u]||l;return n?a.createElement(m,i(i({ref:t},p),{},{components:n})):a.createElement(m,i({ref:t},p))}));function u(e,t){var n=arguments,r=t&&t.mdxType;if("string"==typeof e||r){var l=n.length,i=new Array(l);i[0]=g;var s={};for(var o in t)hasOwnProperty.call(t,o)&&(s[o]=t[o]);s.originalType=e,s.mdxType="string"==typeof e?e:r,i[1]=s;for(var c=2;c<l;c++)i[c]=n[c];return a.createElement.apply(null,i)}return a.createElement.apply(null,n)}g.displayName="MDXCreateElement"},4089:(e,t,n)=>{n.r(t),n.d(t,{contentTitle:()=>i,default:()=>p,frontMatter:()=>l,metadata:()=>s,toc:()=>o});var a=n(7462),r=(n(7294),n(3905));const l={sidebar_label:"agent",title:"agentchat.agent"},i=void 0,s={unversionedId:"reference/agentchat/agent",id:"reference/agentchat/agent",isDocsHomePage:!1,title:"agentchat.agent",description:"Agent Objects",source:"@site/docs/reference/agentchat/agent.md",sourceDirName:"reference/agentchat",slug:"/reference/agentchat/agent",permalink:"/autogen/docs/reference/agentchat/agent",editUrl:"https://github.com/microsoft/autogen/edit/main/website/docs/reference/agentchat/agent.md",tags:[],version:"current",frontMatter:{sidebar_label:"agent",title:"agentchat.agent"},sidebar:"referenceSideBar",previous:{title:"backend_service",permalink:"/autogen/docs/reference/agentchat/service/backend_service"},next:{title:"assistant_agent",permalink:"/autogen/docs/reference/agentchat/assistant_agent"}},o=[{value:"Agent Objects",id:"agent-objects",children:[{value:"__init__",id:"__init__",children:[],level:4},{value:"name",id:"name",children:[],level:4},{value:"send",id:"send",children:[],level:4},{value:"a_send",id:"a_send",children:[],level:4},{value:"receive",id:"receive",children:[],level:4},{value:"a_receive",id:"a_receive",children:[],level:4},{value:"reset",id:"reset",children:[],level:4},{value:"generate_reply",id:"generate_reply",children:[],level:4},{value:"a_generate_reply",id:"a_generate_reply",children:[],level:4}],level:2}],c={toc:o};function p(e){let{components:t,...n}=e;return(0,r.kt)("wrapper",(0,a.Z)({},c,n,{components:t,mdxType:"MDXLayout"}),(0,r.kt)("h2",{id:"agent-objects"},"Agent Objects"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},"class Agent()\n")),(0,r.kt)("p",null,"(In preview) An abstract class for AI agent."),(0,r.kt)("p",null,"An agent can communicate with other agents and perform actions.\nDifferent agents can differ in what actions they perform in the ",(0,r.kt)("inlineCode",{parentName:"p"},"receive")," method."),(0,r.kt)("h4",{id:"__init__"},"_","_","init","_","_"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},"def __init__(name: str)\n")),(0,r.kt)("p",null,(0,r.kt)("strong",{parentName:"p"},"Arguments"),":"),(0,r.kt)("ul",null,(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("inlineCode",{parentName:"li"},"name")," ",(0,r.kt)("em",{parentName:"li"},"str")," - name of the agent.")),(0,r.kt)("h4",{id:"name"},"name"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},"@property\ndef name()\n")),(0,r.kt)("p",null,"Get the name of the agent."),(0,r.kt)("h4",{id:"send"},"send"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},'def send(message: Union[Dict, str],\n         recipient: "Agent",\n         request_reply: Optional[bool] = None)\n')),(0,r.kt)("p",null,"(Abstract method) Send a message to another agent."),(0,r.kt)("h4",{id:"a_send"},"a","_","send"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},'async def a_send(message: Union[Dict, str],\n                 recipient: "Agent",\n                 request_reply: Optional[bool] = None)\n')),(0,r.kt)("p",null,"(Abstract async method) Send a message to another agent."),(0,r.kt)("h4",{id:"receive"},"receive"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},'def receive(message: Union[Dict, str],\n            sender: "Agent",\n            request_reply: Optional[bool] = None)\n')),(0,r.kt)("p",null,"(Abstract method) Receive a message from another agent."),(0,r.kt)("h4",{id:"a_receive"},"a","_","receive"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},'async def a_receive(message: Union[Dict, str],\n                    sender: "Agent",\n                    request_reply: Optional[bool] = None)\n')),(0,r.kt)("p",null,"(Abstract async method) Receive a message from another agent."),(0,r.kt)("h4",{id:"reset"},"reset"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},"def reset()\n")),(0,r.kt)("p",null,"(Abstract method) Reset the agent."),(0,r.kt)("h4",{id:"generate_reply"},"generate","_","reply"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},'def generate_reply(messages: Optional[List[Dict]] = None,\n                   sender: Optional["Agent"] = None,\n                   **kwargs) -> Union[str, Dict, None]\n')),(0,r.kt)("p",null,"(Abstract method) Generate a reply based on the received messages."),(0,r.kt)("p",null,(0,r.kt)("strong",{parentName:"p"},"Arguments"),":"),(0,r.kt)("ul",null,(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("inlineCode",{parentName:"li"},"messages")," ",(0,r.kt)("em",{parentName:"li"},"list","[dict]")," - a list of messages received."),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("inlineCode",{parentName:"li"},"sender")," - sender of an Agent instance.")),(0,r.kt)("p",null,(0,r.kt)("strong",{parentName:"p"},"Returns"),":"),(0,r.kt)("p",null,"  str or dict or None: the generated reply. If None, no reply is generated."),(0,r.kt)("h4",{id:"a_generate_reply"},"a","_","generate","_","reply"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},'async def a_generate_reply(messages: Optional[List[Dict]] = None,\n                           sender: Optional["Agent"] = None,\n                           **kwargs) -> Union[str, Dict, None]\n')),(0,r.kt)("p",null,"(Abstract async method) Generate a reply based on the received messages."),(0,r.kt)("p",null,(0,r.kt)("strong",{parentName:"p"},"Arguments"),":"),(0,r.kt)("ul",null,(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("inlineCode",{parentName:"li"},"messages")," ",(0,r.kt)("em",{parentName:"li"},"list","[dict]")," - a list of messages received."),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("inlineCode",{parentName:"li"},"sender")," - sender of an Agent instance.")),(0,r.kt)("p",null,(0,r.kt)("strong",{parentName:"p"},"Returns"),":"),(0,r.kt)("p",null,"  str or dict or None: the generated reply. If None, no reply is generated."))}p.isMDXComponent=!0}}]);
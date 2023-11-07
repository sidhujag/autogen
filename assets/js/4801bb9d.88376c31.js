"use strict";(self.webpackChunkwebsite=self.webpackChunkwebsite||[]).push([[8603],{3905:(e,t,n)=>{n.d(t,{Zo:()=>i,kt:()=>h});var a=n(7294);function r(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function l(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);t&&(a=a.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,a)}return n}function c(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?l(Object(n),!0).forEach((function(t){r(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):l(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function o(e,t){if(null==e)return{};var n,a,r=function(e,t){if(null==e)return{};var n,a,r={},l=Object.keys(e);for(a=0;a<l.length;a++)n=l[a],t.indexOf(n)>=0||(r[n]=e[n]);return r}(e,t);if(Object.getOwnPropertySymbols){var l=Object.getOwnPropertySymbols(e);for(a=0;a<l.length;a++)n=l[a],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(r[n]=e[n])}return r}var s=a.createContext({}),p=function(e){var t=a.useContext(s),n=t;return e&&(n="function"==typeof e?e(t):c(c({},t),e)),n},i=function(e){var t=p(e.components);return a.createElement(s.Provider,{value:t},e.children)},u={inlineCode:"code",wrapper:function(e){var t=e.children;return a.createElement(a.Fragment,{},t)}},g=a.forwardRef((function(e,t){var n=e.components,r=e.mdxType,l=e.originalType,s=e.parentName,i=o(e,["components","mdxType","originalType","parentName"]),g=p(n),h=r,m=g["".concat(s,".").concat(h)]||g[h]||u[h]||l;return n?a.createElement(m,c(c({ref:t},i),{},{components:n})):a.createElement(m,c({ref:t},i))}));function h(e,t){var n=arguments,r=t&&t.mdxType;if("string"==typeof e||r){var l=n.length,c=new Array(l);c[0]=g;var o={};for(var s in t)hasOwnProperty.call(t,s)&&(o[s]=t[s]);o.originalType=e,o.mdxType="string"==typeof e?e:r,c[1]=o;for(var p=2;p<l;p++)c[p]=n[p];return a.createElement.apply(null,c)}return a.createElement.apply(null,n)}g.displayName="MDXCreateElement"},3927:(e,t,n)=>{n.r(t),n.d(t,{contentTitle:()=>c,default:()=>i,frontMatter:()=>l,metadata:()=>o,toc:()=>s});var a=n(7462),r=(n(7294),n(3905));const l={sidebar_label:"groupchat",title:"agentchat.groupchat"},c=void 0,o={unversionedId:"reference/agentchat/groupchat",id:"reference/agentchat/groupchat",isDocsHomePage:!1,title:"agentchat.groupchat",description:"GroupChat Objects",source:"@site/docs/reference/agentchat/groupchat.md",sourceDirName:"reference/agentchat",slug:"/reference/agentchat/groupchat",permalink:"/autogen/docs/reference/agentchat/groupchat",editUrl:"https://github.com/microsoft/autogen/edit/main/website/docs/reference/agentchat/groupchat.md",tags:[],version:"current",frontMatter:{sidebar_label:"groupchat",title:"agentchat.groupchat"},sidebar:"referenceSideBar",previous:{title:"discoverable_conversable_agent",permalink:"/autogen/docs/reference/agentchat/discoverable_conversable_agent"},next:{title:"user_proxy_agent",permalink:"/autogen/docs/reference/agentchat/user_proxy_agent"}},s=[{value:"GroupChat Objects",id:"groupchat-objects",children:[{value:"agent_names",id:"agent_names",children:[],level:4},{value:"reset",id:"reset",children:[],level:4},{value:"agent_by_name",id:"agent_by_name",children:[],level:4},{value:"next_agent",id:"next_agent",children:[],level:4},{value:"select_speaker_msg",id:"select_speaker_msg",children:[],level:4},{value:"select_speaker",id:"select_speaker",children:[],level:4}],level:2},{value:"GroupChatManager Objects",id:"groupchatmanager-objects",children:[{value:"run_chat",id:"run_chat",children:[],level:4},{value:"a_run_chat",id:"a_run_chat",children:[],level:4}],level:2}],p={toc:s};function i(e){let{components:t,...n}=e;return(0,r.kt)("wrapper",(0,a.Z)({},p,n,{components:t,mdxType:"MDXLayout"}),(0,r.kt)("h2",{id:"groupchat-objects"},"GroupChat Objects"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},"@dataclass\nclass GroupChat()\n")),(0,r.kt)("p",null,"(In preview) A group chat class that contains the following data fields:"),(0,r.kt)("ul",null,(0,r.kt)("li",{parentName:"ul"},"agents: a list of participating agents."),(0,r.kt)("li",{parentName:"ul"},"messages: a list of messages in the group chat."),(0,r.kt)("li",{parentName:"ul"},"max_round: the maximum number of rounds."),(0,r.kt)("li",{parentName:"ul"},'admin_name: the name of the admin agent if there is one. Default is "Admin".\nKeyBoardInterrupt will make the admin agent take over.'),(0,r.kt)("li",{parentName:"ul"},"func_call_filter: whether to enforce function call filter. Default is True.\nWhen set to True and when a message is a function call suggestion,\nthe next speaker will be chosen from an agent which contains the corresponding function name\nin its ",(0,r.kt)("inlineCode",{parentName:"li"},"function_map"),".")),(0,r.kt)("h4",{id:"agent_names"},"agent","_","names"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},"@property\ndef agent_names() -> List[str]\n")),(0,r.kt)("p",null,"Return the names of the agents in the group chat."),(0,r.kt)("h4",{id:"reset"},"reset"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},"def reset()\n")),(0,r.kt)("p",null,"Reset the group chat."),(0,r.kt)("h4",{id:"agent_by_name"},"agent","_","by","_","name"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},"def agent_by_name(name: str) -> Agent\n")),(0,r.kt)("p",null,"Find the next speaker based on the message."),(0,r.kt)("h4",{id:"next_agent"},"next","_","agent"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},"def next_agent(agent: Agent, agents: List[Agent]) -> Agent\n")),(0,r.kt)("p",null,"Return the next agent in the list."),(0,r.kt)("h4",{id:"select_speaker_msg"},"select","_","speaker","_","msg"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},"def select_speaker_msg(agents: List[Agent])\n")),(0,r.kt)("p",null,"Return the message for selecting the next speaker."),(0,r.kt)("h4",{id:"select_speaker"},"select","_","speaker"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},"def select_speaker(last_speaker: Agent, selector: ConversableAgent)\n")),(0,r.kt)("p",null,"Select the next speaker."),(0,r.kt)("h2",{id:"groupchatmanager-objects"},"GroupChatManager Objects"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},"class GroupChatManager(ConversableAgent)\n")),(0,r.kt)("p",null,"(In preview) A chat manager agent that can manage a group chat of multiple agents."),(0,r.kt)("h4",{id:"run_chat"},"run","_","chat"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},"def run_chat(messages: Optional[List[Dict]] = None,\n             sender: Optional[Agent] = None,\n             config: Optional[GroupChat] = None) -> Union[str, Dict, None]\n")),(0,r.kt)("p",null,"Run a group chat."),(0,r.kt)("h4",{id:"a_run_chat"},"a","_","run","_","chat"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},"async def a_run_chat(messages: Optional[List[Dict]] = None,\n                     sender: Optional[Agent] = None,\n                     config: Optional[GroupChat] = None)\n")),(0,r.kt)("p",null,"Run a group chat asynchronously."))}i.isMDXComponent=!0}}]);
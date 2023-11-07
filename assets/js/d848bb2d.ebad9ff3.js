"use strict";(self.webpackChunkwebsite=self.webpackChunkwebsite||[]).push([[7159],{3905:(e,t,n)=>{n.d(t,{Zo:()=>p,kt:()=>d});var a=n(7294);function r(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function l(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);t&&(a=a.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,a)}return n}function i(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?l(Object(n),!0).forEach((function(t){r(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):l(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function o(e,t){if(null==e)return{};var n,a,r=function(e,t){if(null==e)return{};var n,a,r={},l=Object.keys(e);for(a=0;a<l.length;a++)n=l[a],t.indexOf(n)>=0||(r[n]=e[n]);return r}(e,t);if(Object.getOwnPropertySymbols){var l=Object.getOwnPropertySymbols(e);for(a=0;a<l.length;a++)n=l[a],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(r[n]=e[n])}return r}var c=a.createContext({}),s=function(e){var t=a.useContext(c),n=t;return e&&(n="function"==typeof e?e(t):i(i({},t),e)),n},p=function(e){var t=s(e.components);return a.createElement(c.Provider,{value:t},e.children)},m={inlineCode:"code",wrapper:function(e){var t=e.children;return a.createElement(a.Fragment,{},t)}},u=a.forwardRef((function(e,t){var n=e.components,r=e.mdxType,l=e.originalType,c=e.parentName,p=o(e,["components","mdxType","originalType","parentName"]),u=s(n),d=r,f=u["".concat(c,".").concat(d)]||u[d]||m[d]||l;return n?a.createElement(f,i(i({ref:t},p),{},{components:n})):a.createElement(f,i({ref:t},p))}));function d(e,t){var n=arguments,r=t&&t.mdxType;if("string"==typeof e||r){var l=n.length,i=new Array(l);i[0]=u;var o={};for(var c in t)hasOwnProperty.call(t,c)&&(o[c]=t[c]);o.originalType=e,o.mdxType="string"==typeof e?e:r,i[1]=o;for(var s=2;s<l;s++)i[s]=n[s];return a.createElement.apply(null,i)}return a.createElement.apply(null,n)}u.displayName="MDXCreateElement"},6002:(e,t,n)=>{n.r(t),n.d(t,{contentTitle:()=>i,default:()=>p,frontMatter:()=>l,metadata:()=>o,toc:()=>c});var a=n(7462),r=(n(7294),n(3905));const l={sidebar_label:"text_analyzer_agent",title:"agentchat.contrib.text_analyzer_agent"},i=void 0,o={unversionedId:"reference/agentchat/contrib/text_analyzer_agent",id:"reference/agentchat/contrib/text_analyzer_agent",isDocsHomePage:!1,title:"agentchat.contrib.text_analyzer_agent",description:"TextAnalyzerAgent Objects",source:"@site/docs/reference/agentchat/contrib/text_analyzer_agent.md",sourceDirName:"reference/agentchat/contrib",slug:"/reference/agentchat/contrib/text_analyzer_agent",permalink:"/autogen/docs/reference/agentchat/contrib/text_analyzer_agent",editUrl:"https://github.com/microsoft/autogen/edit/main/website/docs/reference/agentchat/contrib/text_analyzer_agent.md",tags:[],version:"current",frontMatter:{sidebar_label:"text_analyzer_agent",title:"agentchat.contrib.text_analyzer_agent"},sidebar:"referenceSideBar",previous:{title:"teachable_agent",permalink:"/autogen/docs/reference/agentchat/contrib/teachable_agent"},next:{title:"backend_service",permalink:"/autogen/docs/reference/agentchat/service/backend_service"}},c=[{value:"TextAnalyzerAgent Objects",id:"textanalyzeragent-objects",children:[{value:"__init__",id:"__init__",children:[],level:4},{value:"analyze_text",id:"analyze_text",children:[],level:4}],level:2}],s={toc:c};function p(e){let{components:t,...n}=e;return(0,r.kt)("wrapper",(0,a.Z)({},s,n,{components:t,mdxType:"MDXLayout"}),(0,r.kt)("h2",{id:"textanalyzeragent-objects"},"TextAnalyzerAgent Objects"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},"class TextAnalyzerAgent(ConversableAgent)\n")),(0,r.kt)("p",null,"(Experimental) Text Analysis agent, a subclass of ConversableAgent designed to analyze text as instructed."),(0,r.kt)("h4",{id:"__init__"},"_","_","init","_","_"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},'def __init__(name="analyzer",\n             system_message: Optional[str] = system_message,\n             human_input_mode: Optional[str] = "NEVER",\n             llm_config: Optional[Union[Dict, bool]] = None,\n             **kwargs)\n')),(0,r.kt)("p",null,(0,r.kt)("strong",{parentName:"p"},"Arguments"),":"),(0,r.kt)("ul",null,(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("inlineCode",{parentName:"li"},"name")," ",(0,r.kt)("em",{parentName:"li"},"str")," - name of the agent."),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("inlineCode",{parentName:"li"},"system_message")," ",(0,r.kt)("em",{parentName:"li"},"str")," - system message for the ChatCompletion inference."),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("inlineCode",{parentName:"li"},"human_input_mode")," ",(0,r.kt)("em",{parentName:"li"},"str")," - This agent should NEVER prompt the human for input."),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("inlineCode",{parentName:"li"},"llm_config")," ",(0,r.kt)("em",{parentName:"li"},"dict or False")," - llm inference configuration.\nPlease refer to ",(0,r.kt)("a",{parentName:"li",href:"/docs/reference/oai/client#create"},"OpenAIWrapper.create"),"\nfor available options.\nTo disable llm-based auto reply, set to False."),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("inlineCode",{parentName:"li"},"teach_config")," ",(0,r.kt)("em",{parentName:"li"},"dict or None")," - Additional parameters used by TeachableAgent.\nTo use default config, set to None. Otherwise, set to a dictionary with any of the following keys:",(0,r.kt)("ul",{parentName:"li"},(0,r.kt)("li",{parentName:"ul"},"verbosity (Optional, int): # 0 (default) for basic info, 1 to add memory operations, 2 for analyzer messages, 3 for memo lists."),(0,r.kt)("li",{parentName:"ul"},"reset_db (Optional, bool): True to clear the DB before starting. Default False."),(0,r.kt)("li",{parentName:"ul"},'path_to_db_dir (Optional, str): path to the directory where the DB is stored. Default "./tmp/teachable_agent_db"'),(0,r.kt)("li",{parentName:"ul"},"prepopulate (Optional, int): True (default) to prepopulate the DB with a set of input-output pairs."),(0,r.kt)("li",{parentName:"ul"},"recall_threshold (Optional, float): The maximum distance for retrieved memos, where 0.0 is exact match. Default 1.5. Larger values allow more (but less relevant) memos to be recalled."),(0,r.kt)("li",{parentName:"ul"},"max_num_retrievals (Optional, int): The maximum number of memos to retrieve from the DB. Default 10."))),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("inlineCode",{parentName:"li"},"**kwargs")," ",(0,r.kt)("em",{parentName:"li"},"dict")," - other kwargs in ",(0,r.kt)("a",{parentName:"li",href:"../conversable_agent#__init__"},"ConversableAgent"),".")),(0,r.kt)("h4",{id:"analyze_text"},"analyze","_","text"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},"def analyze_text(text_to_analyze, analysis_instructions)\n")),(0,r.kt)("p",null,"Analyzes the given text as instructed, and returns the analysis."))}p.isMDXComponent=!0}}]);
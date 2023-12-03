"use strict";(self.webpackChunkwebsite=self.webpackChunkwebsite||[]).push([[6386],{3905:(e,r,t)=>{t.d(r,{Zo:()=>o,kt:()=>h});var n=t(7294);function a(e,r,t){return r in e?Object.defineProperty(e,r,{value:t,enumerable:!0,configurable:!0,writable:!0}):e[r]=t,e}function c(e,r){var t=Object.keys(e);if(Object.getOwnPropertySymbols){var n=Object.getOwnPropertySymbols(e);r&&(n=n.filter((function(r){return Object.getOwnPropertyDescriptor(e,r).enumerable}))),t.push.apply(t,n)}return t}function s(e){for(var r=1;r<arguments.length;r++){var t=null!=arguments[r]?arguments[r]:{};r%2?c(Object(t),!0).forEach((function(r){a(e,r,t[r])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(t)):c(Object(t)).forEach((function(r){Object.defineProperty(e,r,Object.getOwnPropertyDescriptor(t,r))}))}return e}function i(e,r){if(null==e)return{};var t,n,a=function(e,r){if(null==e)return{};var t,n,a={},c=Object.keys(e);for(n=0;n<c.length;n++)t=c[n],r.indexOf(t)>=0||(a[t]=e[t]);return a}(e,r);if(Object.getOwnPropertySymbols){var c=Object.getOwnPropertySymbols(e);for(n=0;n<c.length;n++)t=c[n],r.indexOf(t)>=0||Object.prototype.propertyIsEnumerable.call(e,t)&&(a[t]=e[t])}return a}var p=n.createContext({}),l=function(e){var r=n.useContext(p),t=r;return e&&(t="function"==typeof e?e(r):s(s({},r),e)),t},o=function(e){var r=l(e.components);return n.createElement(p.Provider,{value:r},e.children)},u={inlineCode:"code",wrapper:function(e){var r=e.children;return n.createElement(n.Fragment,{},r)}},g=n.forwardRef((function(e,r){var t=e.components,a=e.mdxType,c=e.originalType,p=e.parentName,o=i(e,["components","mdxType","originalType","parentName"]),g=l(t),h=a,d=g["".concat(p,".").concat(h)]||g[h]||u[h]||c;return t?n.createElement(d,s(s({ref:r},o),{},{components:t})):n.createElement(d,s({ref:r},o))}));function h(e,r){var t=arguments,a=r&&r.mdxType;if("string"==typeof e||a){var c=t.length,s=new Array(c);s[0]=g;var i={};for(var p in r)hasOwnProperty.call(r,p)&&(i[p]=r[p]);i.originalType=e,i.mdxType="string"==typeof e?e:a,s[1]=i;for(var l=2;l<c;l++)s[l]=t[l];return n.createElement.apply(null,s)}return n.createElement.apply(null,t)}g.displayName="MDXCreateElement"},9129:(e,r,t)=>{t.r(r),t.d(r,{contentTitle:()=>s,default:()=>o,frontMatter:()=>c,metadata:()=>i,toc:()=>p});var n=t(7462),a=(t(7294),t(3905));const c={sidebar_label:"search_engine_serpapi",title:"agentchat.service.search_engine_serpapi"},s=void 0,i={unversionedId:"reference/agentchat/service/search_engine_serpapi",id:"reference/agentchat/service/search_engine_serpapi",isDocsHomePage:!1,title:"agentchat.service.search_engine_serpapi",description:"@Time   27",source:"@site/docs/reference/agentchat/service/search_engine_serpapi.md",sourceDirName:"reference/agentchat/service",slug:"/reference/agentchat/service/search_engine_serpapi",permalink:"/autogen/docs/reference/agentchat/service/search_engine_serpapi",editUrl:"https://github.com/microsoft/autogen/edit/main/website/docs/reference/agentchat/service/search_engine_serpapi.md",tags:[],version:"current",frontMatter:{sidebar_label:"search_engine_serpapi",title:"agentchat.service.search_engine_serpapi"},sidebar:"referenceSideBar",previous:{title:"search_engine_googleapi",permalink:"/autogen/docs/reference/agentchat/service/search_engine_googleapi"},next:{title:"search_engine_serper",permalink:"/autogen/docs/reference/agentchat/service/search_engine_serper"}},p=[{value:"SerpAPIWrapper Objects",id:"serpapiwrapper-objects",children:[{value:"search_engine",id:"search_engine",children:[],level:4},{value:"run",id:"run",children:[],level:4},{value:"results",id:"results",children:[],level:4},{value:"get_params",id:"get_params",children:[],level:4}],level:2}],l={toc:p};function o(e){let{components:r,...t}=e;return(0,a.kt)("wrapper",(0,n.Z)({},l,t,{components:r,mdxType:"MDXLayout"}),(0,a.kt)("p",null,"@Time    : 2023/5/23 18:27\n@Author  : alexanderwu\n@File    : search_engine_serpapi.py"),(0,a.kt)("h2",{id:"serpapiwrapper-objects"},"SerpAPIWrapper Objects"),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-python"},"class SerpAPIWrapper(BaseModel)\n")),(0,a.kt)("h4",{id:"search_engine"},"search","_","engine"),(0,a.kt)("p",null,":meta private:"),(0,a.kt)("h4",{id:"run"},"run"),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-python"},"@staticmethod\nasync def run(query, max_results: int = 8, as_string: bool = True) -> str\n")),(0,a.kt)("p",null,"Run query through SerpAPI and parse result async."),(0,a.kt)("h4",{id:"results"},"results"),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-python"},"async def results(query: str, max_results: int) -> dict\n")),(0,a.kt)("p",null,"Use aiohttp to run query through SerpAPI and return the results async."),(0,a.kt)("h4",{id:"get_params"},"get","_","params"),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-python"},"def get_params(query: str) -> Dict[str, str]\n")),(0,a.kt)("p",null,"Get parameters for SerpAPI."))}o.isMDXComponent=!0}}]);
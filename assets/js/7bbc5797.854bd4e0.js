"use strict";(self.webpackChunkwebsite=self.webpackChunkwebsite||[]).push([[7589],{3905:(e,r,t)=>{t.d(r,{Zo:()=>s,kt:()=>b});var n=t(7294);function a(e,r,t){return r in e?Object.defineProperty(e,r,{value:t,enumerable:!0,configurable:!0,writable:!0}):e[r]=t,e}function i(e,r){var t=Object.keys(e);if(Object.getOwnPropertySymbols){var n=Object.getOwnPropertySymbols(e);r&&(n=n.filter((function(r){return Object.getOwnPropertyDescriptor(e,r).enumerable}))),t.push.apply(t,n)}return t}function o(e){for(var r=1;r<arguments.length;r++){var t=null!=arguments[r]?arguments[r]:{};r%2?i(Object(t),!0).forEach((function(r){a(e,r,t[r])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(t)):i(Object(t)).forEach((function(r){Object.defineProperty(e,r,Object.getOwnPropertyDescriptor(t,r))}))}return e}function c(e,r){if(null==e)return{};var t,n,a=function(e,r){if(null==e)return{};var t,n,a={},i=Object.keys(e);for(n=0;n<i.length;n++)t=i[n],r.indexOf(t)>=0||(a[t]=e[t]);return a}(e,r);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(e);for(n=0;n<i.length;n++)t=i[n],r.indexOf(t)>=0||Object.prototype.propertyIsEnumerable.call(e,t)&&(a[t]=e[t])}return a}var l=n.createContext({}),p=function(e){var r=n.useContext(l),t=r;return e&&(t="function"==typeof e?e(r):o(o({},r),e)),t},s=function(e){var r=p(e.components);return n.createElement(l.Provider,{value:r},e.children)},g={inlineCode:"code",wrapper:function(e){var r=e.children;return n.createElement(n.Fragment,{},r)}},u=n.forwardRef((function(e,r){var t=e.components,a=e.mdxType,i=e.originalType,l=e.parentName,s=c(e,["components","mdxType","originalType","parentName"]),u=p(t),b=a,w=u["".concat(l,".").concat(b)]||u[b]||g[b]||i;return t?n.createElement(w,o(o({ref:r},s),{},{components:t})):n.createElement(w,o({ref:r},s))}));function b(e,r){var t=arguments,a=r&&r.mdxType;if("string"==typeof e||a){var i=t.length,o=new Array(i);o[0]=u;var c={};for(var l in r)hasOwnProperty.call(r,l)&&(c[l]=r[l]);c.originalType=e,c.mdxType="string"==typeof e?e:a,o[1]=c;for(var p=2;p<i;p++)o[p]=t[p];return n.createElement.apply(null,o)}return n.createElement.apply(null,t)}u.displayName="MDXCreateElement"},6282:(e,r,t)=>{t.r(r),t.d(r,{contentTitle:()=>o,default:()=>s,frontMatter:()=>i,metadata:()=>c,toc:()=>l});var n=t(3117),a=(t(7294),t(3905));const i={sidebar_label:"web_browser_engine_playwright",title:"agentchat.service.web_browser_engine_playwright"},o=void 0,c={unversionedId:"reference/agentchat/service/web_browser_engine_playwright",id:"reference/agentchat/service/web_browser_engine_playwright",isDocsHomePage:!1,title:"agentchat.service.web_browser_engine_playwright",description:"PlaywrightWrapper Objects",source:"@site/docs/reference/agentchat/service/web_browser_engine_playwright.md",sourceDirName:"reference/agentchat/service",slug:"/reference/agentchat/service/web_browser_engine_playwright",permalink:"/autogen/docs/reference/agentchat/service/web_browser_engine_playwright",editUrl:"https://github.com/microsoft/autogen/edit/main/website/docs/reference/agentchat/service/web_browser_engine_playwright.md",tags:[],version:"current",frontMatter:{sidebar_label:"web_browser_engine_playwright",title:"agentchat.service.web_browser_engine_playwright"},sidebar:"referenceSideBar",previous:{title:"search_engine_serper",permalink:"/autogen/docs/reference/agentchat/service/search_engine_serper"},next:{title:"zapier_service",permalink:"/autogen/docs/reference/agentchat/service/zapier_service"}},l=[{value:"PlaywrightWrapper Objects",id:"playwrightwrapper-objects",children:[],level:2}],p={toc:l};function s(e){let{components:r,...t}=e;return(0,a.kt)("wrapper",(0,n.Z)({},p,t,{components:r,mdxType:"MDXLayout"}),(0,a.kt)("h2",{id:"playwrightwrapper-objects"},"PlaywrightWrapper Objects"),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-python"},"class PlaywrightWrapper()\n")),(0,a.kt)("p",null,"Wrapper around Playwright."),(0,a.kt)("p",null,"To use this module, you should have the ",(0,a.kt)("inlineCode",{parentName:"p"},"playwright")," Python package installed and ensure that\nthe required browsers are also installed. You can install playwright by running the command\n",(0,a.kt)("inlineCode",{parentName:"p"},"pip install metagpt[playwright]")," and download the necessary browser binaries by running the\ncommand ",(0,a.kt)("inlineCode",{parentName:"p"},"playwright install")," for the first time."))}s.isMDXComponent=!0}}]);
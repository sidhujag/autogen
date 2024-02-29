"use strict";(self.webpackChunkwebsite=self.webpackChunkwebsite||[]).push([[58],{7876:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>c,contentTitle:()=>r,default:()=>h,frontMatter:()=>s,metadata:()=>o,toc:()=>d});var i=n(5893),l=n(1151);const s={sidebar_label:"retrieve_utils",title:"retrieve_utils"},r=void 0,o={id:"reference/retrieve_utils",title:"retrieve_utils",description:"UNSTRUCTURED\\_FORMATS",source:"@site/docs/reference/retrieve_utils.md",sourceDirName:"reference",slug:"/reference/retrieve_utils",permalink:"/autogen/docs/reference/retrieve_utils",draft:!1,unlisted:!1,editUrl:"https://github.com/microsoft/autogen/edit/main/website/docs/reference/retrieve_utils.md",tags:[],version:"current",frontMatter:{sidebar_label:"retrieve_utils",title:"retrieve_utils"},sidebar:"referenceSideBar",previous:{title:"math_utils",permalink:"/autogen/docs/reference/math_utils"},next:{title:"serper_utils",permalink:"/autogen/docs/reference/serper_utils"}},c={},d=[{value:"UNSTRUCTURED_FORMATS",id:"unstructured_formats",level:4},{value:"split_text_to_chunks",id:"split_text_to_chunks",level:3},{value:"extract_text_from_pdf",id:"extract_text_from_pdf",level:3},{value:"split_files_to_chunks",id:"split_files_to_chunks",level:3},{value:"get_files_from_dir",id:"get_files_from_dir",level:3},{value:"get_file_from_url",id:"get_file_from_url",level:3},{value:"is_url",id:"is_url",level:3},{value:"create_vector_db_from_dir",id:"create_vector_db_from_dir",level:3},{value:"query_vector_db",id:"query_vector_db",level:3}];function a(e){const t={code:"code",em:"em",h3:"h3",h4:"h4",li:"li",p:"p",pre:"pre",strong:"strong",ul:"ul",...(0,l.a)(),...e.components};return(0,i.jsxs)(i.Fragment,{children:[(0,i.jsx)(t.h4,{id:"unstructured_formats",children:"UNSTRUCTURED_FORMATS"}),"\n",(0,i.jsx)(t.p,{children:"These formats will be parsed by the 'unstructured' library, if installed."}),"\n",(0,i.jsx)(t.h3,{id:"split_text_to_chunks",children:"split_text_to_chunks"}),"\n",(0,i.jsx)(t.pre,{children:(0,i.jsx)(t.code,{className:"language-python",children:'def split_text_to_chunks(text: str,\n                         max_tokens: int = 4000,\n                         chunk_mode: str = "multi_lines",\n                         must_break_at_empty_line: bool = True,\n                         overlap: int = 10)\n'})}),"\n",(0,i.jsx)(t.p,{children:"Split a long text into chunks of max_tokens."}),"\n",(0,i.jsx)(t.h3,{id:"extract_text_from_pdf",children:"extract_text_from_pdf"}),"\n",(0,i.jsx)(t.pre,{children:(0,i.jsx)(t.code,{className:"language-python",children:"def extract_text_from_pdf(file: str) -> str\n"})}),"\n",(0,i.jsx)(t.p,{children:"Extract text from PDF files"}),"\n",(0,i.jsx)(t.h3,{id:"split_files_to_chunks",children:"split_files_to_chunks"}),"\n",(0,i.jsx)(t.pre,{children:(0,i.jsx)(t.code,{className:"language-python",children:'def split_files_to_chunks(files: list,\n                          max_tokens: int = 4000,\n                          chunk_mode: str = "multi_lines",\n                          must_break_at_empty_line: bool = True,\n                          custom_text_split_function: Callable = None)\n'})}),"\n",(0,i.jsx)(t.p,{children:"Split a list of files into chunks of max_tokens."}),"\n",(0,i.jsx)(t.h3,{id:"get_files_from_dir",children:"get_files_from_dir"}),"\n",(0,i.jsx)(t.pre,{children:(0,i.jsx)(t.code,{className:"language-python",children:"def get_files_from_dir(dir_path: Union[str, List[str]],\n                       types: list = TEXT_FORMATS,\n                       recursive: bool = True)\n"})}),"\n",(0,i.jsx)(t.p,{children:"Return a list of all the files in a given directory, a url, a file path or a list of them."}),"\n",(0,i.jsx)(t.h3,{id:"get_file_from_url",children:"get_file_from_url"}),"\n",(0,i.jsx)(t.pre,{children:(0,i.jsx)(t.code,{className:"language-python",children:"def get_file_from_url(url: str, save_path: str = None)\n"})}),"\n",(0,i.jsx)(t.p,{children:"Download a file from a URL."}),"\n",(0,i.jsx)(t.h3,{id:"is_url",children:"is_url"}),"\n",(0,i.jsx)(t.pre,{children:(0,i.jsx)(t.code,{className:"language-python",children:"def is_url(string: str)\n"})}),"\n",(0,i.jsx)(t.p,{children:"Return True if the string is a valid URL."}),"\n",(0,i.jsx)(t.h3,{id:"create_vector_db_from_dir",children:"create_vector_db_from_dir"}),"\n",(0,i.jsx)(t.pre,{children:(0,i.jsx)(t.code,{className:"language-python",children:'def create_vector_db_from_dir(dir_path: Union[str, List[str]],\n                              max_tokens: int = 4000,\n                              client: API = None,\n                              db_path: str = "/tmp/chromadb.db",\n                              collection_name: str = "all-my-documents",\n                              get_or_create: bool = False,\n                              chunk_mode: str = "multi_lines",\n                              must_break_at_empty_line: bool = True,\n                              embedding_model: str = "all-MiniLM-L6-v2",\n                              embedding_function: Callable = None,\n                              custom_text_split_function: Callable = None,\n                              custom_text_types: List[str] = TEXT_FORMATS,\n                              recursive: bool = True,\n                              extra_docs: bool = False) -> API\n'})}),"\n",(0,i.jsx)(t.p,{children:"Create a vector db from all the files in a given directory, the directory can also be a single file or a url to\na single file. We support chromadb compatible APIs to create the vector db, this function is not required if\nyou prepared your own vector db."}),"\n",(0,i.jsxs)(t.p,{children:[(0,i.jsx)(t.strong,{children:"Arguments"}),":"]}),"\n",(0,i.jsxs)(t.ul,{children:["\n",(0,i.jsxs)(t.li,{children:[(0,i.jsx)(t.code,{children:"dir_path"})," ",(0,i.jsx)(t.em,{children:"Union[str, List[str]]"})," - the path to the directory, file, url or a list of them."]}),"\n",(0,i.jsxs)(t.li,{children:[(0,i.jsx)(t.code,{children:"max_tokens"})," ",(0,i.jsx)(t.em,{children:"Optional, int"})," - the maximum number of tokens per chunk. Default is 4000."]}),"\n",(0,i.jsxs)(t.li,{children:[(0,i.jsx)(t.code,{children:"client"})," ",(0,i.jsx)(t.em,{children:"Optional, API"})," - the chromadb client. Default is None."]}),"\n",(0,i.jsxs)(t.li,{children:[(0,i.jsx)(t.code,{children:"db_path"})," ",(0,i.jsx)(t.em,{children:"Optional, str"}),' - the path to the chromadb. Default is "/tmp/chromadb.db".']}),"\n",(0,i.jsxs)(t.li,{children:[(0,i.jsx)(t.code,{children:"collection_name"})," ",(0,i.jsx)(t.em,{children:"Optional, str"}),' - the name of the collection. Default is "all-my-documents".']}),"\n",(0,i.jsxs)(t.li,{children:[(0,i.jsx)(t.code,{children:"get_or_create"})," ",(0,i.jsx)(t.em,{children:"Optional, bool"})," - Whether to get or create the collection. Default is False. If True, the collection\nwill be returned if it already exists. Will raise ValueError if the collection already exists and get_or_create is False."]}),"\n",(0,i.jsxs)(t.li,{children:[(0,i.jsx)(t.code,{children:"chunk_mode"})," ",(0,i.jsx)(t.em,{children:"Optional, str"}),' - the chunk mode. Default is "multi_lines".']}),"\n",(0,i.jsxs)(t.li,{children:[(0,i.jsx)(t.code,{children:"must_break_at_empty_line"})," ",(0,i.jsx)(t.em,{children:"Optional, bool"})," - Whether to break at empty line. Default is True."]}),"\n",(0,i.jsxs)(t.li,{children:[(0,i.jsx)(t.code,{children:"embedding_model"})," ",(0,i.jsx)(t.em,{children:"Optional, str"}),' - the embedding model to use. Default is "all-MiniLM-L6-v2". Will be ignored if\nembedding_function is not None.']}),"\n",(0,i.jsxs)(t.li,{children:[(0,i.jsx)(t.code,{children:"embedding_function"})," ",(0,i.jsx)(t.em,{children:"Optional, Callable"})," - the embedding function to use. Default is None, SentenceTransformer with\nthe given ",(0,i.jsx)(t.code,{children:"embedding_model"})," will be used. If you want to use OpenAI, Cohere, HuggingFace or other embedding\nfunctions, you can pass it here, follow the examples in ",(0,i.jsx)(t.code,{children:"https://docs.trychroma.com/embeddings"}),"."]}),"\n",(0,i.jsxs)(t.li,{children:[(0,i.jsx)(t.code,{children:"custom_text_split_function"})," ",(0,i.jsx)(t.em,{children:"Optional, Callable"})," - a custom function to split a string into a list of strings.\nDefault is None, will use the default function in ",(0,i.jsx)(t.code,{children:"autogen.retrieve_utils.split_text_to_chunks"}),"."]}),"\n",(0,i.jsxs)(t.li,{children:[(0,i.jsx)(t.code,{children:"custom_text_types"})," ",(0,i.jsx)(t.em,{children:"Optional, List[str]"})," - a list of file types to be processed. Default is TEXT_FORMATS."]}),"\n",(0,i.jsxs)(t.li,{children:[(0,i.jsx)(t.code,{children:"recursive"})," ",(0,i.jsx)(t.em,{children:"Optional, bool"})," - whether to search documents recursively in the dir_path. Default is True."]}),"\n",(0,i.jsxs)(t.li,{children:[(0,i.jsx)(t.code,{children:"extra_docs"})," ",(0,i.jsx)(t.em,{children:"Optional, bool"})," - whether to add more documents in the collection. Default is False"]}),"\n"]}),"\n",(0,i.jsxs)(t.p,{children:[(0,i.jsx)(t.strong,{children:"Returns"}),":"]}),"\n",(0,i.jsx)(t.p,{children:"The chromadb client."}),"\n",(0,i.jsx)(t.h3,{id:"query_vector_db",children:"query_vector_db"}),"\n",(0,i.jsx)(t.pre,{children:(0,i.jsx)(t.code,{className:"language-python",children:'def query_vector_db(query_texts: List[str],\n                    n_results: int = 10,\n                    client: API = None,\n                    db_path: str = "/tmp/chromadb.db",\n                    collection_name: str = "all-my-documents",\n                    search_string: str = "",\n                    embedding_model: str = "all-MiniLM-L6-v2",\n                    embedding_function: Callable = None) -> QueryResult\n'})}),"\n",(0,i.jsx)(t.p,{children:"Query a vector db. We support chromadb compatible APIs, it's not required if you prepared your own vector db\nand query function."}),"\n",(0,i.jsxs)(t.p,{children:[(0,i.jsx)(t.strong,{children:"Arguments"}),":"]}),"\n",(0,i.jsxs)(t.ul,{children:["\n",(0,i.jsxs)(t.li,{children:[(0,i.jsx)(t.code,{children:"query_texts"})," ",(0,i.jsx)(t.em,{children:"List[str]"})," - the list of strings which will be used to query the vector db."]}),"\n",(0,i.jsxs)(t.li,{children:[(0,i.jsx)(t.code,{children:"n_results"})," ",(0,i.jsx)(t.em,{children:"Optional, int"})," - the number of results to return. Default is 10."]}),"\n",(0,i.jsxs)(t.li,{children:[(0,i.jsx)(t.code,{children:"client"})," ",(0,i.jsx)(t.em,{children:"Optional, API"})," - the chromadb compatible client. Default is None, a chromadb client will be used."]}),"\n",(0,i.jsxs)(t.li,{children:[(0,i.jsx)(t.code,{children:"db_path"})," ",(0,i.jsx)(t.em,{children:"Optional, str"}),' - the path to the vector db. Default is "/tmp/chromadb.db".']}),"\n",(0,i.jsxs)(t.li,{children:[(0,i.jsx)(t.code,{children:"collection_name"})," ",(0,i.jsx)(t.em,{children:"Optional, str"}),' - the name of the collection. Default is "all-my-documents".']}),"\n",(0,i.jsxs)(t.li,{children:[(0,i.jsx)(t.code,{children:"search_string"})," ",(0,i.jsx)(t.em,{children:"Optional, str"}),' - the search string. Only docs that contain an exact match of this string will be retrieved. Default is "".']}),"\n",(0,i.jsxs)(t.li,{children:[(0,i.jsx)(t.code,{children:"embedding_model"})," ",(0,i.jsx)(t.em,{children:"Optional, str"}),' - the embedding model to use. Default is "all-MiniLM-L6-v2". Will be ignored if\nembedding_function is not None.']}),"\n",(0,i.jsxs)(t.li,{children:[(0,i.jsx)(t.code,{children:"embedding_function"})," ",(0,i.jsx)(t.em,{children:"Optional, Callable"})," - the embedding function to use. Default is None, SentenceTransformer with\nthe given ",(0,i.jsx)(t.code,{children:"embedding_model"})," will be used. If you want to use OpenAI, Cohere, HuggingFace or other embedding\nfunctions, you can pass it here, follow the examples in ",(0,i.jsx)(t.code,{children:"https://docs.trychroma.com/embeddings"}),"."]}),"\n"]}),"\n",(0,i.jsxs)(t.p,{children:[(0,i.jsx)(t.strong,{children:"Returns"}),":"]}),"\n",(0,i.jsx)(t.p,{children:"The query result. The format is:"}),"\n",(0,i.jsx)(t.pre,{children:(0,i.jsx)(t.code,{className:"language-python",children:"class QueryResult(TypedDict):\n    ids: List[IDs]\n    embeddings: Optional[List[List[Embedding]]]\n    documents: Optional[List[List[Document]]]\n    metadatas: Optional[List[List[Metadata]]]\n    distances: Optional[List[List[float]]]\n"})})]})}function h(e={}){const{wrapper:t}={...(0,l.a)(),...e.components};return t?(0,i.jsx)(t,{...e,children:(0,i.jsx)(a,{...e})}):a(e)}},1151:(e,t,n)=>{n.d(t,{Z:()=>o,a:()=>r});var i=n(7294);const l={},s=i.createContext(l);function r(e){const t=i.useContext(s);return i.useMemo((function(){return"function"==typeof e?e(t):{...t,...e}}),[t,e])}function o(e){let t;return t=e.disableParentContext?"function"==typeof e.components?e.components(l):e.components||l:r(e.components),i.createElement(s.Provider,{value:t},e.children)}}}]);
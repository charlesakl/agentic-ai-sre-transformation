from pathlib import Path
import os
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

ROOT=Path(__file__).resolve().parent.parent
def load_documents():
    return [Document(page_content=p.read_text(encoding="utf-8"),
            metadata={"doc_id":p.stem,"source":p.name,"kind":"synthetic"})
            for p in sorted((ROOT/"knowledge").glob("*.md"))]

def retrieve_knowledge(query,k=3):
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY required for vector embeddings")
    store=Chroma(collection_name="sre-demo-phase3b-v1",
                 embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"),
                 persist_directory=str(ROOT/".chroma"))
    if store._collection.count()==0:
        docs=load_documents()
        store.add_documents(docs,ids=[d.metadata["doc_id"] for d in docs])
    results=store.similarity_search_with_score(query,k=k)
    return [{"doc_id":d.metadata["doc_id"],"source":d.metadata["source"],
             "content":d.page_content,"distance":float(score)} for d,score in results]

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import pandas as pd
import json
import os

with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\memory.json","r") as f:
    data=json.load(f);

df=pd.DataFrame(data)
embeddings=OllamaEmbeddings(model="mxbai-embed-large")
db_location="./memory_langchain_db"

vector_store=Chroma(
    collection_name="memory",
    persist_directory=db_location,
    embedding_function=embeddings
)

existing_ids = set(vector_store.get()["ids"])


documents=[]
ids=[]
for i,row in df.iterrows():
    doc_id = f"{row['data_type']}_{i}"
    if doc_id not in existing_ids:
        document=Document(
            page_content=row["fact"],
            metadata={
                "doc_id":i,
                "source":row["data_type"]+str(i),
                "chunk_index":i
            },  
        )
        ids.append(doc_id)
        documents.append(document)




if documents:
    vector_store.add_documents(documents=documents,ids=ids)
    print(f"Added {len(documents)} new chunks.")
else:
    print("No new chunks found — DB already up to date.")

memory_retriever=vector_store.as_retriever(
    search_kwargs={"k":3}
)


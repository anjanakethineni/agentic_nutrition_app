import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFDirectoryLoader, DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

DATA_PATH = "./data"
PERSIST_PATH = "./chroma_db"

def ingest_documents():
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
        print(f"Created '{DATA_PATH}' folder. Place your diet PDF and TXT files there.")
        return

    print("Loading documents...")
    pdf_loader = PyPDFDirectoryLoader(DATA_PATH)
    txt_loader = DirectoryLoader(DATA_PATH, glob="*.txt", loader_cls=TextLoader)
    
    docs = pdf_loader.load() + txt_loader.load()
    if not docs:
        print(f"No files found in '{DATA_PATH}'. Add your PDFs/TXT files and re-run.")
        return

    print(f"Loaded {len(docs)} document pages/files.")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = text_splitter.split_documents(docs)
    print(f"Split into {len(chunks)} text chunks.")

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=PERSIST_PATH
    )
    print(f"Successfully saved vector index to '{PERSIST_PATH}'.")

if __name__ == "__main__":
    ingest_documents()
import os
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from langchain.chat_models import ChatOpenAI
from pydantic import BaseModel

# Load environment variables from .env file (if any)
load_dotenv()
import os

from langchain.chains.question_answering import load_qa_chain
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter


def document_loader(docs_path):
    """_summary_

    Args:
        docs_path (pdf): To load Pdf documents

    Returns:
        _type_: pages of a
    """
    loader = PyPDFLoader(docs_path)
    pages = loader.load_and_split()
    return pages


def split_docs(documents, chunk_size=1000, chunk_overlap=20):
    """_summary_

    Args:
        documents (_type_): _description_
        chunk_size (int, optional): _description_. Defaults to 1000.
        chunk_overlap (int, optional): _description_. Defaults to 20.

    Returns:
        _type_: _description_
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    docs = text_splitter.split_documents(documents)
    return docs


class Response(BaseModel):
    result: str | None


class Request(BaseModel):
    question: str | None
    pdf_name: str | None


origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://pratikllm.centralindia.cloudapp.azure.com",
    "98.70.73.159",
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/file")
async def upload_file(file: UploadFile = File(...)):
    # Do here your stuff with the file
    try:
        with open(f"uploaded_files/{file.filename}", "wb") as f:
            f.write(await file.read())
    except Exception as e:
        return {"result": f"Uploading failed due to `{e}`"}
    return {"filename": file.filename}


@app.post("/api/predict")
async def predict(request: Request) -> Any:
    if not os.path.exists(f"uploaded_files/{request.pdf_name}"):
        return JSONResponse(status_code=500, content={"result": "Load the pdf first"})
    documents = document_loader(f"uploaded_files/{request.pdf_name}")
    docs = split_docs(documents)
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    db = Chroma.from_documents(docs, embeddings)
    persist_directory = "chroma_db"

    vectordb = Chroma.from_documents(documents=docs, embedding=embeddings, persist_directory=persist_directory)
    vectordb.persist()
    os.environ["OPENAI_API_KEY"] = "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"
    model_name = "gpt-3.5-turbo"
    llm = ChatOpenAI(model_name=model_name)
    chain = load_qa_chain(llm, chain_type="stuff", verbose=True)
    matching_docs = db.similarity_search(f"uploaded_files/{request.question}")
    answer = chain.run(input_documents=matching_docs, question=f"uploaded_files/{request.question}")
    return {"result": f"{answer}"}



# Commented out IPython magic to ensure Python compatibility.
!pip install langchain_community
# %pip install langchain-together

import pandas as pd
import numpy as np
from langchain_together import ChatTogether
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate
from langchain_core.messages import SystemMessage
from pydantic import BaseModel
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.chains import RetrievalQAWithSourcesChain

model = ChatTogether(model = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
                     api_key = "tgp_v1_frWMlsoybz07FVkKvUwHnvuekBp2yQ7u7BX4Kl5bjd0")

book = "FinalOmarCv.pdf"

loader = PyPDFLoader(book)
books = loader.load()

rc_spliter = RecursiveCharacterTextSplitter(
    separators= ["\n\n","\n","."," "],
    chunk_size=1000,
    chunk_overlap=100,
)
docs = rc_spliter.split_documents(books)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2") 

vector_store = Chroma.from_documents(docs, embeddings)

Retrival = vector_store.as_retriever(
    search_type = "similarity",
    search_kwargs = {"k":2}
)

template = ChatPromptTemplate.from_messages(
    [
    SystemMessage(content = "You Are a pdf reader that when human asks you something in his uploaded cv you retrive info using rag"),
    ("system", "You have to make sure that the pdf are read correctly"),
    ("system","you have to make sure to make the retrived info a good situation"),
    ("human","find this info in the book {info}"),
    ("ai","Here are the answer {answer}")
]
)

def Rag(Question):
  retrieved_docs = Retrival.invoke(Question)
  formatted_input = {"info": Question, "answer": retrieved_docs}
  Rag_chain = template | model
  return Rag_chain.invoke(formatted_input)

print(Rag("What is the Objective?").content)

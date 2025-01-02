import os

from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAI
from langchain_openai.embeddings import OpenAIEmbeddings

load_dotenv()  # load the environment variables


class Rag:
    def __init__(self, path):
        self.doc_path = path  # path to the directory contianuing the text files

    def embedding(self, top_k=4):
        embeddings = OpenAIEmbeddings()
        # store the embedded data into a vector database
        vector_store = Chroma.from_documents(
            self._ingest(),
            embeddings,
        )
        return vector_store.as_retriever(top_k=top_k)

    def _ingest(self, chunk_size=128, chunk_overlap=32, separator="\n"):
        file_texts = []  # list of document objects
        for file in os.listdir(self.doc_path):
            with open(f"{self.doc_path}/{file}") as f:
                file_text = f.read()
            text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=chunk_size, chunk_overlap=chunk_overlap, separator=separator
            )
            texts = text_splitter.split_text(file_text)
            for idx, chunked_text in enumerate(texts):
                file_texts.append(
                    Document(
                        page_content=chunked_text,
                        metadata={
                            "doc_title": file.split(".")[0],
                            "chunk_num": idx,
                        },
                    )
                )
        return file_texts


class Llm:
    def __init__(self, path="./docs"):
        self.embedding = Rag(path).embedding()
        self.openai = OpenAI()

    def ask(self, prompt):
        chain = (
            {"context": self.embedding, "question": RunnablePassthrough()}
            | self._create_template()
            | self.openai
            | StrOutputParser()
        )
        return chain.invoke(prompt)

    def _create_template(self):
        template = """You are Lucy, a helpful AI assistant. The tone I'd like you to use is a bit light-hearted, casual,
        enthusiastic, and informal. Use the following pieces to retrieve context to
        answer the question.

        Question: {question}

        Context:  {context}

        If you don't know the answer, just say you don't know the answer.

        Answer:
        """
        return ChatPromptTemplate.from_template(template)

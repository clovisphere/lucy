import os
from typing import Any

from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings


class Rag:
    def __init__(self, path: str, logger: Any) -> None:
        self.directory_path = path  # path to the directory containing the text files
        self.logger = logger

    def etl(self) -> None:
        self.logger.debug("ETL 😊")
        vector_store = FAISS.from_documents(
            documents=self._injest_pdf_documents(),
            embedding=OpenAIEmbeddings(
                model=os.getenv("OPENAI_EMBEDDING_MODEL") or "text-embedding-3-large"
            ),
        )
        self.logger.debug("Saving indexed files to vector store")
        vector_store.save_local(os.getenv("VECTOR_STORE") or "./.vector_store")

    @staticmethod
    def get_vector_store() -> FAISS:
        return FAISS.load_local(
            folder_path=os.getenv("VECTOR_STORE") or "./.vector_store",
            embeddings=OpenAIEmbeddings(
                model=os.getenv("OPENAI_EMBEDDING_MODEL") or "text-embedding-3-large"
            ),
            allow_dangerous_deserialization=True,
        )

    def _injest_pdf_documents(
        self, chunk_size: int = 1000, chunk_overlap: int = 0
    ) -> list[Document]:
        self.logger.debug("Preparing files that need to be indexed 🤭")
        docs: list[Document] = []
        for file in os.listdir(self.directory_path):
            if not file.endswith(".pdf"):
                continue  # skip non-pdf files
            docs.extend(PyPDFLoader(f"{self.directory_path}/{file}").load())
        # Split the documents into chunks
        text_splitter = CharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap, separator="\n"
        )
        self.logger.debug("Process completed 👏🏽", files_indexed=len(docs))
        return text_splitter.split_documents(docs)

    # The following code is an alternative implementation of
    # the _injest_*_documents method.
    # It uses the text_splitter to split the .txt files into chunks.
    #
    # **NOTE:** IT IS NOT USED IN THE CURRENT IMPLEMENTATION OF THE RAG CLASS 😞
    def _injest_txt_documents(
        self, chunk_size: int = 128, chunk_overlap: int = 32, separator: str = "\n"
    ) -> list[Document]:
        self.logger.debug("Preparing files that need to be indexed 🤭")
        docs: list[Document] = []  # list of document objects
        for file in os.listdir(self.directory_path):
            with open(f"{self.directory_path}/{file}") as f:
                if not file.endswith(".txt"):
                    continue  # skip non-txt files
                file_text = f.read()
            text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=chunk_size, chunk_overlap=chunk_overlap, separator=separator
            )
            texts = text_splitter.split_text(file_text)
            for idx, chunked_text in enumerate(texts):
                docs.append(
                    Document(
                        page_content=chunked_text,
                        metadata={
                            "doc_title": file.split(".")[0],
                            "chunk_num": idx,
                        },
                    )
                )
        self.logger.debug("Process completed 👏🏽", files_indexed=len(docs))
        return docs

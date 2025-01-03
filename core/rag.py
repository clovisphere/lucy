import os

from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings


class Rag:
    def __init__(self, path: str) -> None:
        self.directory_path = path  # path to the directory containing the text files
        self.store_path = os.getenv("VECTOR_STORE_PATH") or "./vector_store"

    @property
    def embedding(self) -> OpenAIEmbeddings:
        return OpenAIEmbeddings(
            model=os.getenv("OPENAI_EMBEDDING_MODEL") or "text-embedding-3-large"
        )

    def etl(self) -> None:
        try:
            store: FAISS = FAISS.from_documents(
                documents=self._get_documents(), embedding=self.embedding
            )
            store.save_local(self.store_path)
        except Exception as e:
            print(f"> An exception occurred [ETL] - {e}")

    def get_store(self) -> FAISS:
        return FAISS.load_local(
            folder_path=self.store_path,
            embeddings=self.embedding,
            allow_dangerous_deserialization=True,
        )

    def _get_documents(
        self, chunk_size: int = 890, chunk_overlap: int = 35
    ) -> list[Document]:
        docs: list[Document] = []
        for file in os.listdir(self.directory_path):
            try:
                docs.extend(PyPDFLoader(f"{self.directory_path}/{file}").load())
            except Exception as e:
                print(f"> An exception occurred [PDF] - {e}")
        # Split the documents into chunks
        text_splitter = CharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap, separator="\n"
        )
        return text_splitter.split_documents(docs)

    # The following code is an alternative implementation of the documents property
    # It uses the text_splitter to split the text into chunks

    # @property
    # def documents(
    #     self, chunk_size: int = 128, chunk_overlap: int = 32, separator: str = "\n"
    # ) -> list[Document]:
    #     file_texts: list[Document] = []  # list of document objects
    #     for file in os.listdir(self.doc_path):
    #         with open(f"{self.doc_path}/{file}") as f:
    #             file_text = f.read()
    #         text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    #             chunk_size=chunk_size, chunk_overlap=chunk_overlap, separator=separator
    #         )
    #         texts = text_splitter.split_text(file_text)
    #         for idx, chunked_text in enumerate(texts):
    #             file_texts.append(
    #                 Document(
    #                     page_content=chunked_text,
    #                     metadata={
    #                         "doc_title": file.split(".")[0],
    #                         "chunk_num": idx,
    #                     },
    #                 )
    #             )
    #     return file_texts

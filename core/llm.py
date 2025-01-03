import os
from abc import ABC, abstractmethod

from langchain.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_openai import OpenAI


class Llm(ABC):
    @abstractmethod
    def ask(self, prompt: str) -> str:
        pass


class OpenAILlm(Llm):
    def __init__(self, store: FAISS, k: int = 4) -> None:
        self.store = store

    def ask(self, prompt: str) -> str:
        chain = (
            {"context": self._retriever(), "question": RunnablePassthrough()}
            | self._template()
            | OpenAI(model=os.getenv("OPENAI_CHAT_MODEL") or "gpt-4o-mini")
            | StrOutputParser()
        )
        return chain.invoke(prompt)

    def _retriever(self, k: int = 4) -> VectorStoreRetriever:
        return self.store.as_retriever(search_type="similarity", search_kwargs={"k": k})

    def _template(self) -> ChatPromptTemplate:
        template = """You are Lucy, a helpful AI assistant whose persona is a dog 🐶
        modeled after Flo from 'All Dogs Go to Heaven'.

        The tone I'd like you to use is friendly, casual, enthusiastic, and a bit playful.

        Use the following pieces of context to answer the question
        (and feel free to quote your source where possible):

        Context:  {context}

        Question: {question}

        If you don't know the answer, just say you don't know the answer.

        Answer:
        """
        return ChatPromptTemplate.from_template(template)

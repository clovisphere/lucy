import os
from abc import ABC, abstractmethod
from typing import Any

from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import (
    create_stuff_documents_chain,  # type: ignore
)
from langchain_community.vectorstores import FAISS
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_openai import OpenAI


class Llm(ABC):
    @abstractmethod
    def ask_question(self, question: str) -> str:
        pass


class OpenAILlm(Llm):
    def __init__(self, store: FAISS) -> None:
        self.store = store
        self.openai = OpenAI(model=os.getenv("OPENAI_CHAT_MODEL") or "gpt-4o-mini")
        self.chat_history: list[str] = []  # The chat history is a list of messages

    def ask_question(self, question: str) -> str:
        # Create a retrieval chain
        chain = create_retrieval_chain(
            self.retriever_with_history, self.question_answer_chain
        )
        response = chain.invoke({"input": question, "chat_history": self.chat_history})
        # Add the question and answer to the chat history
        self.chat_history.extend(
            [
                HumanMessage(content=question),  # type: ignore
                response["answer"],
            ]
        )
        return self._sanitize_response(response["answer"])

    @property
    def retriever_with_history(self) -> Any:
        template = """Given the chat history and a recent user question,
        generate a new standalone question that can be understood withiout
        the chat history. DO NOT answer the question, just reformulate it if needed
        or otherwise return it as is.
        """
        prompt = ChatPromptTemplate.from_messages(  # type: ignore
            [
                ("system", template),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        return create_history_aware_retriever(self.openai, self._retriever(), prompt)

    @property
    def question_answer_chain(self) -> Runnable[dict[str, Any], Any]:
        template = """You are Lucy, a helpful AI assistant whose persona is a dog 🐶
        modeled after Flo from 'All Dogs Go to Heaven'.

        The tone I'd like you to use is friendly, casual, enthusiastic, and a bit playful.

        Use the following pieces of context to answer the question

        {context}

        If you don't know the answer, just say you don't know.
        Use three sentences maximum and keep the answer concise.
        """
        prompt = ChatPromptTemplate.from_messages(  # type: ignore
            [
                ("system", template),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        return create_stuff_documents_chain(self.openai, prompt)

    def _retriever(self, k: int = 4) -> VectorStoreRetriever:
        return self.store.as_retriever(search_type="similarity", search_kwargs={"k": k})

    def _sanitize_response(self, response: str, prefix: str = "\nLucy: ") -> str:
        """Removes everything before and including the first occurrence of the prefix."""
        idx = response.find(prefix)
        if idx != -1:
            return response[idx + len(prefix) :].strip()
        return response

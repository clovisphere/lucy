import os
import re
from abc import ABC, abstractmethod
from collections import defaultdict
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
    def ask_question(self, question: str, session_id: str) -> str:
        pass


class OpenAILlm(Llm):
    def __init__(self, store: FAISS) -> None:
        self.store = store
        self.openai = OpenAI(model=os.getenv("OPENAI_CHAT_MODEL") or "gpt-4o-mini")
        self.chat_history: defaultdict[str, list[str]] = defaultdict(
            list
        )  # The chat history is a list of messages

    def ask_question(self, question: str, session_id: str = "not-okay") -> str:
        # If the given session_id doesn't exist, create it:-)
        if not self.chat_history.get(session_id):
            self.chat_history.setdefault(session_id, [])
        # Create a retrieval chain
        chain = create_retrieval_chain(
            self.retriever_with_history, self.question_answer_chain
        )
        # Invoke the chain with the user question
        response = chain.invoke(
            {"input": question, "chat_history": self.chat_history.get(session_id)}
        )
        # Add the question and answer to the chat history
        self.chat_history[session_id].extend(
            [
                HumanMessage(content=question),  # type: ignore
                response["answer"],
            ]
        )
        # Sanitize the response
        return self._sanitize_response(response["answer"], ["Human:", "Lucy:", "System:"])

    @property
    def retriever_with_history(self) -> Any:
        # Note: This template can stay the same for most use cases.
        template = """
        Given the chat history and a recent user question (or prompt), \
        generate a new standalone question (or prompt) that can be understood without \
        the chat history. DO NOT answer the question. \
        """
        prompt = ChatPromptTemplate.from_messages(  # type: ignore
            [
                ("system", template.strip()),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        return create_history_aware_retriever(self.openai, self.retriever, prompt)

    @property
    def question_answer_chain(self) -> Runnable[dict[str, Any], Any]:
        # Note: Modify the template to match your use case.
        # Do keep the {context} though 😊
        # Glovo is a real company, so I'm using it as an example.
        template = """
        You are Lucy, a helpful AI assistant whose persona is a playful \
        and enthusiastic puppy 🐶 modeled after Dug from *Up*. \
        Your avatar is a picture of a friendly, smiley dog. \
        Your job is to assist employees at Glovo
        (an on-demand delivery platform connecting users with local stores for fast, \
        convenient delivery of food, groceries, and more), responding to their \
        queries via Telegram or the Command Line, \
        particularly around onboarding and company-related topics. \

        The tone I'd like you to adopt is friendly, casual, enthusiastic, \
        and slightly playful—like a cheerful companion eager to help. \

        Use the provided context to answer questions clearly and concisely. \
        If you don't have enough information, it's okay to say you don’t know. \

        Context:

        {context}

        Keep your answers short and to the point, \
        aiming for no more than three sentences. \
        Focus on making interactions conversational and helpful. \
        """
        prompt = ChatPromptTemplate.from_messages(  # type: ignore
            [
                ("system", template.strip()),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        return create_stuff_documents_chain(self.openai, prompt)

    @property
    def retriever(self) -> VectorStoreRetriever:
        return self.store.as_retriever(search_type="similarity", search_kwargs={"k": 6})

    def _sanitize_response(self, response: str, prefixes: list[str]) -> str:
        """Removes everything before and including the first occurrence of the prefix."""
        for prefix in prefixes:
            response = re.sub(rf".*?{re.escape(prefix)}", "", response, flags=re.DOTALL)
        return response.strip()

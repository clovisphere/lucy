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

from app.config import settings


class Llm(ABC):
    @abstractmethod
    def ask_question(self, question: str, session_id: str) -> str:
        pass


class OpenAILlm(Llm):
    def __init__(self, store: FAISS, logger: Any) -> None:
        self.store = store
        self.openai = OpenAI(model=os.getenv("OPENAI_CHAT_MODEL") or "gpt-4o-mini")
        self.chat_history: defaultdict[str, list[str]] = defaultdict(
            list
        )  # The chat history is a list of messages
        self.logger = logger

    def ask_question(self, question: str, session_id: str = "not-okay") -> str:
        self.logger.info(
            "About to answer user's question", question=question, session_id=session_id
        )
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
        self.logger.debug("AI 🤖 (raw) response 🙂", response=response)
        # Add the question and answer to the chat history
        self.chat_history[session_id].extend(
            [
                HumanMessage(content=question),  # type: ignore
                response["answer"],
            ]
        )
        self.logger.debug(
            "Updating chat history", chat_history=self.chat_history, session_id=session_id
        )
        # Sanitize the response
        return self._sanitize_response(
            response["answer"], ["Human:", "Lucy:", "System:"], session_id
        )

    @property
    def retriever_with_history(self) -> Any:
        prompt = ChatPromptTemplate.from_messages(  # type: ignore
            [
                ("system", settings.SYSTEM_TEMPLATE.strip()),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        return create_history_aware_retriever(self.openai, self.retriever, prompt)

    @property
    def question_answer_chain(self) -> Runnable[dict[str, Any], Any]:
        prompt = ChatPromptTemplate.from_messages(  # type: ignore
            [
                ("system", settings.LLM_TEMPLATE.strip()),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        return create_stuff_documents_chain(self.openai, prompt)

    @property
    def retriever(self) -> VectorStoreRetriever:
        return self.store.as_retriever(search_type="similarity", search_kwargs={"k": 6})

    def _sanitize_response(
        self, response: str, prefixes: list[str], session_id: str
    ) -> str:
        """Removes everything before and including the first occurrence of the prefix."""
        self.logger.debug(
            "Unsanitized response 😒", response=response, session_id=session_id
        )
        for prefix in prefixes:
            response = re.sub(rf".*?{re.escape(prefix)}", "", response, flags=re.DOTALL)
        self.logger.info(
            "Sanitized llm's response 🥳", response=response, session_id=session_id
        )
        return response.strip()

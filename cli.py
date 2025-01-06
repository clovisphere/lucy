import logging
from contextlib import contextmanager
from typing import Any

import click
from art import tprint  # type: ignore
from dotenv import load_dotenv
from structlog.testing import capture_logs

from app.helpers.llm import OpenAILlm
from app.helpers.logger import log
from app.helpers.rag import Rag

load_dotenv()  # load the environment variables

# Little hack 😊 to suppress 'faiss.loader' and 'httpx' INFO logs
logging.getLogger("faiss.loader").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


@contextmanager
@click.command()
@click.option(
    "--path",
    default="./docs",
    help="Path to the directory containing the documents to index.",
)
@click.option(
    "--command",
    type=click.Choice(["index", "repl"], case_sensitive=False),
    help="What do you want to do?\n"
    "\nindex: Generate the index for the AI assistant."
    "\nrepl:  Ask the AI assistant question via a REPL.",
)
def console(path: str, command: str) -> None:
    # When running in CLI mode,
    # no need to show logs
    with capture_logs():
        click.echo(tprint("Lucy", font="tarty7"))
        if command == "index":
            index_files(path, log)
        else:
            click.echo("Starting the REPL...")
            start_repl(OpenAILlm(Rag.get_vector_store(), log))
        # Is this what you call self promotion? 😂
        click.secho(
            "\nCrafted with ❤️ by ©️ clovisphere (https://github.com/clovisphere)",
            fg="bright_black",
        )


def index_files(path: str, log: Any) -> None:
    click.secho("Indexing...", fg="blue")
    # TODO: Add progress bar here to show the progress of the indexing
    _ = Rag(path, log).etl()
    click.secho("Indexing complete! 🎉", fg="green")


def start_repl(llm: OpenAILlm) -> None:
    click.secho(
        "\nI'm Lucy 🐶, a helpful AI assistant. You can ask me anything.", fg="blue"
    )
    click.secho("Type 'exit', 'quit', or 'q' to leave the REPL.\n", fg="red")

    while True and ((prompt := input("You: ")) not in ["exit", "quit", "q"]):
        ai_answer = llm.ask_question(prompt)
        click.secho(f"> {ai_answer.strip()}", fg="bright_cyan")
    # Leaving us already? 😪
    click.secho(
        "\nOh noooo! 🐾 You're leaving already? 😪🥺 I'll be here, tail wagging, "
        "howling for your return.. woof, woof 🐕",
        fg="red",
    )


# This is the entry point of the CLI
if __name__ == "__main__":
    console()

import click
from art import tprint  # type: ignore

from core.llm import OpenAILlm
from core.rag import Rag


@click.command()
@click.option(
    "--path", default="./docs", help="Path to the directory containing the documents."
)
@click.option(
    "--command",
    type=click.Choice(["index", "repl"], case_sensitive=False),
    help="What do you want to do?\n"
    "\nindex: Generate the index for the AI assistant."
    "\nrepl:  Ask the AI assistant question via a REPL.",
)
def console(path: str, command: str) -> None:
    click.echo(tprint("Lucy", font="tarty7"))

    rag: Rag = Rag(path)
    if command == "index":
        indexing(rag)
    else:
        click.echo("Starting the REPL...")
        start_repl(OpenAILlm(rag.get_store()))
    # Is this what you call self promotion? 😂
    click.secho(
        "\nCrafted with ❤️ by " "©️ clovisphere (https://github.com/clovisphere)",
        fg="bright_black",
    )


def indexing(rag: Rag):
    click.secho("Indexing the documents...", fg="blue")
    rag.etl()
    click.secho("Indexing complete! 🎉", fg="green")


def start_repl(openai: OpenAILlm) -> None:
    click.secho(
        "\nI'm Lucy 🐶, a helpful AI assistant. " "You can ask me anything.", fg="blue"
    )
    click.secho("Type 'exit', 'quit', or 'q' to leave the REPL.\n", fg="red")

    while True and ((prompt := input("You: ")) not in ["exit", "quit", "q"]):
        response = openai.ask_question(prompt)
        click.secho(f"> {response.strip()}", fg="bright_cyan")
    click.secho(
        "\nOh noooo! 🐾 You're leaving already? 🥺 I'll be here, tail wagging, "
        "howling for your return.. woof, woof 🐕",
        fg="red",
    )


if __name__ == "__main__":
    console()

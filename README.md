![Ask Lucy](./images/Lucy.png)

Lucy is an AI assistant designed to help you find answers by querying a pre-built index of documents, such as your company's knowledge base.
She’s perfect for onboarding new employees, answering FAQs, or even planning a party!

Lucy primarily works through a CLI but can also integrate with platforms like Telegram, WhatsApp, and more.

> **Note**: This project is in its early stages, so expect continuous updates and improvements. 😅


## TODO
- [ ] Telegram integration
- [ ] Caching (we need to cache chat history)
- [ ] Unit Tests (super **IMPORTANT**)
- [ ] Logging (mostly for debugging purposes)
- [ ] CI/CD (GitHub Actions, maybe?)
- [ ] Dockerize the app
- [ ] Deployment (Digital Ocean, AWS, GCP, etc.)

Nice to have 😊

- [ ] Telemetry/Observability ([prometheus](https://prometheus.io/), anyone?)
- [ ] (a possible) web app (we'll see about this one 😉)
- [ ] WhatsApp business integration (why not?)
- [ ] Conquer the world 🌍 and sell it for a couple of million dollars 💰 (just kidding 😂)

## Requirements

- Python 3.13
- OpenAI API key
- Patience and a lot of coffee ☕️... (that's optional, though 😅)

## Usage

Before you can use the CLI, you need to set up the environment variables,
so make a copy of [.env.local](./.env.local) and rename it to `.env`. Fill in the necessary values.

### CLI

```
Usage: cli.py [OPTIONS]

Options:
  --path TEXT             Path to the directory containing the documents to
                          index.
  --command [index|repl]  What do you want to do?

                          index: Generate the index for the AI assistant.
                          repl:  Ask the AI assistant question via a REPL.

  --help                  Show this message and exit.
```

#### Development 👷🏽

```console
$ uv run cli.py --path='./docs' --command='index'  # index all documents found in ./docs
$ uv run cli.py --command='repl'                   # start repl (query your document with the help of Lucy 🐶)
```

## Author

Clovis Mugaruka :-)

- [BlueSky](https://bsky.app/profile/clovisphere.github.io)
- [GitHub](https://github.com/clovisphere)


## Acknowledgements

The work is inspired by [ada](https://github.com/MercuryTechnologies/ada)
created by the talented team at [Mercury](https://mercury.com/). If anyone deserves credit,
it's them—props to Mercury! (And oh, they made me (re)learn [Haskell](https://people.willamette.edu/~fruehr/haskell/evolution.html)) 👏🏽

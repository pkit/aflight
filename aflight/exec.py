from aflight.__main__ import Cli

if __name__ == "__main__":
    cli = Cli()
    app = cli.load_app()
    app.execute()

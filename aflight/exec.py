import sys

from aflight.__main__ import Cli

if __name__ == "__main__":
    cli = Cli()
    app = cli.load_app()
    cmd, = sys.argv[1:2] or ['']
    app.execute(command=cmd.encode("utf-8"))

import typer

from commands.instructions import app as instructions_app

app = typer.Typer(help="维护 agents workflow 能力。", no_args_is_help=True)
app.add_typer(instructions_app, name="instructions")


def main() -> None:
    app()

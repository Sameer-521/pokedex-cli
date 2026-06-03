from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

COMMANDS = [
    ("/info <name...>", "Display full dashboard for one or more Pokémon by name"),
    (
        "/info-id <id...>",
        "Display full dashboard for one or more Pokémon by Pokédex ID",
    ),
    ("/cmp <name_a> <name_b>", "Side-by-side stat comparison with color-coded diff"),
    ("/abilities", "List all abilities in a paginated table"),
    ("/ability <name>", "Show ability description and Pokémon that have it"),
    ("/type-matchup", "Display the full 18×18 type effectiveness chart"),
    ("/clear", "Clear the terminal screen"),
    ("/help", "Show this help message"),
]


def display_help() -> None:
    table = Table(title="Available Commands", expand=False)
    table.add_column("Command", style="bold cyan", no_wrap=True)
    table.add_column("Description", style="white")

    for cmd, desc in COMMANDS:
        table.add_row(cmd, desc)

    console.print(
        Panel(
            table,
            title="[bold yellow]HELP[/bold yellow]",
            expand=False,
        )
    )

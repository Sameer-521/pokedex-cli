from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from cmdline import (
    print_abilities,
    print_ability_info,
    print_comparison,
    print_dashboard,
    print_evolution_info,
    print_pokemon_list,
    print_type_map,
)
from data import (
    BASE_IMAGES_PATH,
    MAX_POKEDEX_ID,
    abilities_df,
    ability_by_name,
    ability_owners,
    by_type,
    evolves_from,
    evolves_to,
    pokemon_by_id,
    pokemon_by_name,
    pokemon_names,
    records,
    type_chart_df,
)

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
    ("/evo <name>", "Show evolution chain and conditions for a Pokémon"),
    ("/list [type]", "List Pokémon, optionally filtered by type"),
    ("/clear", "Clear the terminal screen"),
    ("/help", "Show this help message"),
    ("/exit, /quit", "Leave the Pokédex"),
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


def handle_info(args: list[str]) -> None:
    if len(args) == 0:
        print("Please specify pokemon(s) name(s)")
        return
    invalid_names = {name for name in args if name not in pokemon_names}
    if invalid_names:
        print(f"Invalid names: {invalid_names}")
    for name in set(args) - invalid_names:
        pokemon_info = pokemon_by_name[name]
        img_path = BASE_IMAGES_PATH / (
            str(pokemon_info["pokedex_id"]).zfill(4) + ".png"
        )
        print_dashboard(img_path, pokemon_info)


def handle_info_by_id(args: list[str]) -> None:
    if len(args) == 0:
        print("Please enter a valid pokemon ID")
        return
    valid_ids: set[int] = set()
    invalid: list[str] = []
    for token in args:
        try:
            pokedex_id = int(token)
        except ValueError:
            invalid.append(token)
            continue
        if 1 <= pokedex_id <= MAX_POKEDEX_ID:
            valid_ids.add(pokedex_id)
        else:
            invalid.append(token)
    if invalid:
        print(f"Invalid IDs: {invalid}")
    for pokedex_id in sorted(valid_ids):
        pokemon_info = pokemon_by_id[pokedex_id]
        img_path = BASE_IMAGES_PATH / (str(pokedex_id).zfill(4) + ".png")
        print_dashboard(img_path, pokemon_info)


def handle_cmp(args: list[str]) -> None:
    if len(args) < 2:
        print("Please enter two pokemon names")
        return
    pokemon_a, pokemon_b = args[0].lower(), args[1].lower()
    invalid = [name for name in (pokemon_a, pokemon_b) if name not in pokemon_names]
    if invalid:
        print(f"Invalid pokemon name(s): {invalid}")
        return
    print_comparison(pokemon_by_name[pokemon_a], pokemon_by_name[pokemon_b])


def handle_abilities() -> None:
    print_abilities(abilities_df[["id", "name"]].to_dict(orient="records"))


def handle_ability(args: list[str]) -> None:
    if len(args) == 0:
        print("Please specify ability.")
        return
    if len(args) > 1:
        print("You can only view info for one ability at a time.")
        return
    ability = args[0]
    if ability not in ability_by_name:
        print(f"Invalid ability: {ability}")
        return
    print_ability_info(ability_by_name[ability], ability_owners.get(ability, []))


def handle_type_matchup() -> None:
    print_type_map(type_chart_df)


def _chain_lines(root: str, target: str) -> list[str]:
    def label(name: str) -> str:
        return f"[bold]{name.upper()}[/bold]" if name == target else name

    lines: list[str] = []
    stack: list[tuple[str, list[str]]] = [(root, [root])]
    while stack:
        name, path = stack.pop()
        children = evolves_to.get(name)
        if not children:
            lines.append(" → ".join(label(chain_name) for chain_name in path))
            continue
        for child, _ in reversed(children):
            stack.append((child, [*path, child]))
    return lines


def handle_evo(args: list[str]) -> None:
    if len(args) == 0:
        print("Please specify a pokemon name")
        return
    name = args[0].lower()
    if name not in pokemon_names:
        print(f"Invalid pokemon name: {args[0]}")
        return

    parent = evolves_from.get(name)
    children = evolves_to.get(name, [])
    if parent is None and not children:
        console.print(f"[yellow]No evolution data found for '{name}'.[/yellow]")
        return

    root = name
    while root in evolves_from:
        root = evolves_from[root][0]

    conditions: list[str] = []
    if parent is not None:
        parent_name, condition = parent
        conditions.append(
            f"{parent_name} → {name}: {condition}"
            if condition
            else f"{parent_name} → {name}"
        )
    for child, condition in children:
        conditions.append(
            f"{name} → {child}: {condition}" if condition else f"{name} → {child}"
        )

    pokedex_id = pokemon_by_name[name]["pokedex_id"]
    print_evolution_info(pokedex_id, name, _chain_lines(root, name), conditions)


def handle_list(args: list[str]) -> None:
    if args:
        pokemon_type = args[0].lower()
        pokemons = by_type.get(pokemon_type)
        if pokemons is None:
            print(f"Invalid type: {args[0]}")
            print(f"Valid types: {', '.join(sorted(by_type))}")
            return
    else:
        pokemons = records
    print_pokemon_list(pokemons)

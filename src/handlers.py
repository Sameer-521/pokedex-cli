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


def handle_info(rem: list[str]) -> None:
    if len(rem) == 0:
        print("Please specify pokemon(s) name(s)")
        return
    invalid_names = {name for name in rem if name not in pokemon_names}
    if invalid_names:
        print(f"Invalid names: {invalid_names}")
    for name in set(rem) - invalid_names:
        pokemon_info = pokemon_by_name[name]
        img_path = BASE_IMAGES_PATH / (
            str(pokemon_info["pokedex_id"]).zfill(4) + ".png"
        )
        print_dashboard(img_path, pokemon_info)


def handle_info_by_id(rem: list[str]) -> None:
    if len(rem) == 0:
        print("Please enter a valid pokemon ID")
        return
    valid_ids: set[int] = set()
    invalid: list[str] = []
    for token in rem:
        try:
            pid = int(token)
        except ValueError:
            invalid.append(token)
            continue
        if 1 <= pid <= MAX_POKEDEX_ID:
            valid_ids.add(pid)
        else:
            invalid.append(token)
    if invalid:
        print(f"Invalid IDs: {invalid}")
    for pid in sorted(valid_ids):
        pokemon_info = pokemon_by_id[pid]
        img_path = BASE_IMAGES_PATH / (str(pid).zfill(4) + ".png")
        print_dashboard(img_path, pokemon_info)


def handle_cmp(rem: list[str]) -> None:
    if len(rem) < 2:
        print("Please enter two pokemon names")
        return
    pokemon_a, pokemon_b = rem[0].lower(), rem[1].lower()
    invalid = [n for n in (pokemon_a, pokemon_b) if n not in pokemon_names]
    if invalid:
        print(f"Invalid pokemon name(s): {invalid}")
        return
    print_comparison(pokemon_by_name[pokemon_a], pokemon_by_name[pokemon_b])


def handle_abilities() -> None:
    print_abilities(abilities_df[["id", "name"]].to_dict(orient="records"))


def handle_ability(rem: list[str]) -> None:
    if len(rem) == 0:
        print("Please specify ability.")
        return
    if len(rem) > 1:
        print("You can only view info for one ability at a time.")
        return
    ability = rem[0]
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
            lines.append(" → ".join(label(p) for p in path))
            continue
        for child, _ in reversed(children):
            stack.append((child, [*path, child]))
    return lines


def handle_evo(rem: list[str]) -> None:
    if len(rem) == 0:
        print("Please specify a pokemon name")
        return
    name = rem[0].lower()
    if name not in pokemon_names:
        print(f"Invalid pokemon name: {rem[0]}")
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
        src, cond = parent
        conditions.append(f"{src} → {name}: {cond}" if cond else f"{src} → {name}")
    for child, cond in children:
        conditions.append(f"{name} → {child}: {cond}" if cond else f"{name} → {child}")

    pokedex_id = pokemon_by_name[name]["pokedex_id"]
    print_evolution_info(pokedex_id, name, _chain_lines(root, name), conditions)


def handle_list(rem: list[str]) -> None:
    if rem:
        pokemon_type = rem[0].lower()
        pokemons = by_type.get(pokemon_type)
        if pokemons is None:
            print(f"Invalid type: {rem[0]}")
            print(f"Valid types: {', '.join(sorted(by_type))}")
            return
    else:
        pokemons = records
    print_pokemon_list(pokemons)

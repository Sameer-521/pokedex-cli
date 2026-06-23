from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import re

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
    ("/clear", "Clear the terminal screen"),
    ("/help", "Show this help message"),
]


def _strip_markup(text: str) -> str:
    return re.sub(r"\[.*?\]", "", text)


_JSON_TO_CSV: dict[str, str] = {
    "farfetch\u2019d": "farfetchd",
    "nidoran\u2640": "nidoran-f",
    "nidoran\u2642": "nidoran-m",
    "mr. mime": "mr-mime",
    "mime jr.": "mime-jr",
    "type: null": "type-null",
}

_CSV_TO_JSON: dict[str, str] = {v: k for k, v in _JSON_TO_CSV.items()}


def _norm_name(name: str) -> str:
    return _JSON_TO_CSV.get(name, name)


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


def _format_condition(evo_details: dict) -> str:
    if not evo_details:
        return ""

    parts: list[str] = []

    if "candy_required" in evo_details:
        parts.append(f"{evo_details['candy_required']} Candy")

    if "item_required" in evo_details:
        parts.append(evo_details["item_required"])

    if evo_details.get("gender_required") == "Male":
        parts.append("Male only")
    elif evo_details.get("gender_required") == "Female":
        parts.append("Female only")

    if evo_details.get("only_evolves_in_daytime"):
        parts.append("Daytime only")
    if evo_details.get("only_evolves_in_nighttime"):
        parts.append("Nighttime only")

    if evo_details.get("must_be_buddy_to_evolve"):
        dist = evo_details.get("buddy_distance_required")
        if dist:
            parts.append(f"Walk {dist}km as buddy")
        else:
            parts.append("Walk as buddy")

    if "lure_required" in evo_details:
        parts.append(evo_details["lure_required"])

    if evo_details.get("no_candy_cost_if_traded"):
        parts.append("No candy if traded")

    if evo_details.get("upside_down"):
        parts.append("Turn upside-down")

    return ", ".join(parts) if parts else ""


def _build_maps(evo_data: dict) -> tuple[dict, dict]:
    forward_map: dict[str, list[dict]] = {}
    backward_map: dict[str, list[tuple[str, dict]]] = {}
    entries = evo_data["pokemon_name"]
    evolutions = evo_data["evolutions"]

    def _add(key: str):
        if key not in forward_map:
            forward_map[key] = []

    for idx in entries:
        source_name = entries[idx].lower()
        src_csv = _norm_name(source_name)
        evo_list = evolutions[idx]

        if not evo_list:
            continue

        _add(source_name)
        if src_csv != source_name:
            _add(src_csv)

        for evo in evo_list:
            target_name = evo["pokemon_name"].lower()
            tgt_csv = _norm_name(target_name)

            existing = any(
                e["pokemon_name"].lower() == target_name
                for e in forward_map[source_name]
            )
            if not existing:
                forward_map[source_name].append(evo)
                if src_csv != source_name:
                    existing_csv = any(
                        e["pokemon_name"].lower() == target_name
                        for e in forward_map[src_csv]
                    )
                    if not existing_csv:
                        forward_map[src_csv].append(evo)

            for key in {target_name, tgt_csv}:
                if key not in backward_map:
                    backward_map[key] = []
                backward_map[key].append((source_name, evo))

    return forward_map, backward_map


def _find_root(name: str, backward_map: dict) -> str:
    visited: set[str] = set()

    def walk(n: str) -> str:
        if n in visited:
            return n
        visited.add(n)
        if n in backward_map:
            return walk(backward_map[n][0][0])
        return n

    return walk(name)


def _build_chain_tree(root_name: str, forward_map: dict) -> dict:
    visited: set[str] = set()

    def build(name: str) -> dict:
        if name in visited:
            return {"name": name, "children": []}
        visited.add(name)

        children: list[dict] = []
        if name in forward_map:
            for evo in forward_map[name]:
                child_name = evo["pokemon_name"].lower()
                child_tree = build(child_name)
                child_tree["details"] = evo
                children.append(child_tree)

        return {"name": name, "children": children}

    return build(root_name)


def _find_node(root: dict, target: str) -> dict | None:
    if root["name"] == target:
        return root
    for child in root.get("children", []):
        found = _find_node(child, target)
        if found:
            return found
    return None


def _contains_target(node: dict, target: str) -> bool:
    if node["name"] == target:
        return True
    return any(_contains_target(c, target) for c in node.get("children", []))


def _chain_lines(
    node: dict, target: str, depth: int = 0, prefix: str = "", sibling_indent: int = 0
) -> list[str]:
    name = node["name"]
    display = f"[bold]{name.upper()}[/bold]" if name == target else name
    children = node.get("children", [])

    if not children:
        if depth == 0:
            return [display]
        return [f"{prefix}{display}"]

    primary = [c for c in children if _contains_target(c, target)]
    others = [c for c in children if not _contains_target(c, target)]
    ordered = primary + others

    first = ordered[0]
    if depth == 0:
        my_indent = len(_strip_markup(display)) + 1
        first_lines = _chain_lines(
            first, target, depth + 1, f"{display} → ", sibling_indent=my_indent
        )
    else:
        new_prefix = f"{prefix}{display} → "
        my_indent = len(_strip_markup(prefix)) + len(_strip_markup(display)) + 1
        first_lines = _chain_lines(
            first, target, depth + 1, new_prefix, sibling_indent=my_indent
        )

    lines = list(first_lines)

    for child in ordered[1:]:
        child_name = child["name"]
        child_display = (
            f"[bold]{child_name.upper()}[/bold]" if child_name == target else child_name
        )
        si = " " * my_indent
        lines.append(f"{si}→ {child_display}")

        for gc in child.get("children", []):
            gc_indent = my_indent + 2 + len(_strip_markup(child_display)) + 1
            gc_lines = _chain_lines(
                gc, target, depth + 2, f"{si}→ ", sibling_indent=gc_indent
            )
            lines.extend(gc_lines)

    return lines


def handle_evo(name: str, df, evo_data: dict) -> None:
    from cmdline import print_evolution_info

    forward_map, backward_map = _build_maps(evo_data)

    lookup_names = {name}
    if name in _CSV_TO_JSON:
        lookup_names.add(_CSV_TO_JSON[name])

    found = False
    for n in lookup_names:
        if n in forward_map or n in backward_map:
            found = True
            break

    if not found:
        console.print(f"[yellow]No evolution data found for '{name}'.[/yellow]")
        return

    root_name = _find_root(name, backward_map)
    root = _build_chain_tree(root_name, forward_map)

    chain_lines = _chain_lines(root, name)

    conditions: list[str] = []
    for n in lookup_names:
        if n in backward_map:
            for src_name, evo in backward_map[n]:
                cond = _format_condition(evo)
                conditions.append(f"{src_name} → {n}: {cond}")
            break

    for n in lookup_names:
        if n in forward_map:
            for evo in forward_map[n]:
                tgt_name = evo["pokemon_name"].lower()
                cond = _format_condition(evo)
                conditions.append(f"{n} → {tgt_name}: {cond}")
            break

    matching = df.query("name == @name")
    pokedex_id: str | int = ""
    if not matching.empty:
        pokedex_id = matching.iloc[0]["pokedex_id"]

    print_evolution_info(pokedex_id, name, chain_lines, conditions)

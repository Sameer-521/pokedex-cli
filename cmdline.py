import plotext as plt
from PIL import Image
from rich_pixels import Pixels
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()
WIDTH = 50
IMG_SIZE = (42, 42)
PROMPT = "[bold red]POK[/bold red][bold orange3]é[/bold orange3][bold yellow]DEX[/bold yellow] [bold grey50]>[/bold grey50][bold white]>[/bold white] "
banner_text = (
    "[bold red] _____   ____  _  __    _____  ________   __   _____ _      _____ [/bold red]\n"
    "[bold red]|  __ \\ / __ \\| |/ /   |  __ \\|  ____\\ \\ / /  / ____| |    |_   _|[/bold red]\n"
    "[bold orange3]| |__) | |  | | ' / ___| |  | | |__   \\ V /  | |    | |      | |  [/bold orange3]\n"
    "[bold yellow]|  ___/| |  | |  < / _ \\ |  | |  __|   > <   | |    | |      | |  [/bold yellow]\n"
    "[bold yellow3]| |    | |__| | . \\  __/ |__| | |____ / . \\  | |____| |____ _| |_ [/bold yellow3]\n"
    "[bold white]|_|     \\____/|_|\\_\\___|_____/|______/_/ \\_\\  \\_____|______|_____|[/bold white]\n"
    "[bold grey50]                                    (POK[/bold grey50][bold red]é[/bold red][bold grey50]DEX)[/bold grey50]\n"
    "       [bold cyan]⚡ SYSTEM READY // VERSION 2026 ⚡[/bold cyan]\n"
)

UNAVAILABLE = (
    "██████╗\n ██╔═══██╗\n ╚═╝  ██╔╝\n    ██╔═╝\n   ██╔╝\n   ╚═╝\n\n   ██╗\n   ╚═╝"
)


def print_banner():
    console.print(banner_text)


def get_prompt() -> str:
    text = console.input(PROMPT).strip()
    return text


def cast_to_str(poke_data: dict) -> dict:
    """Cast the dict values to str type"""
    for key, val in poke_data.items():
        poke_data[key] = str(val)

    return poke_data


def generate_progress_bar(ratio: float, width: int = 20) -> str:
    """
    Generates an ANSI block progress bar string.

    :param ratio: A float between 0.0 and 1.0 (e.g., 20/100 -> 0.2)
    :param width: The total character width of the progress bar itself
    :return: A formatted string representing the progress bar
    """
    # Clamp the ratio between 0.0 and 1.0 to prevent layout breaking
    ratio = max(0.0, min(1.0, ratio))

    # Calculate how many full blocks to fill
    filled_length = int(width * ratio)

    # ANSI Block characters
    full_block = "█"
    empty_block = "░"
    # Construct the bar
    bar = (full_block * filled_length) + (empty_block * (width - filled_length))

    # Format with percentage
    return f"|{bar}|"


def generate_image_widget(image_path: Path, img_size: tuple = IMG_SIZE) -> Pixels:
    """Generates the high-density Braille string from Plotext."""
    try:
        plt.image_plot(image_path)
        img = Image.open(image_path).resize(img_size)
        pixels = Pixels.from_image(img)

        return pixels
    except ModuleNotFoundError:
        console.print("[yellow]Warning:[/yellow] Pillow is not installed")
        return Pixels.from_ascii((UNAVAILABLE))
    except FileNotFoundError:
        console.print("[yellow]Warning:[/yellow] Image file not found")
        return Pixels.from_ascii((UNAVAILABLE))
    except Exception as e:
        console.print(f"[red]Error in {generate_image_widget.__name__}:[/red] {e}")
        return Pixels.from_ascii((UNAVAILABLE))


def extract_extra_text(poke_data: dict) -> str:

    # Helper function to scale stats for the progress bar (max base stat roughly 160)
    def get_stat_bar(stat_key, max_val=160):
        val = float(poke_data.get(stat_key, 0))
        # Clamp ratio between 0.0 and 1.0
        ratio = min(max(val / max_val, 0.0), 1.0)
        return f"{int(val)} {generate_progress_bar(ratio)}"

    extra_text = (
        f"[bold magenta]No. {poke_data.get('pokedex_id', '???')} — {poke_data.get('genus', 'Unknown')}[/bold magenta]\n"
        f"[bold]Type:[/bold] {poke_data.get('type_1', 'Normal').title()}"
        + (
            f" / {poke_data.get('type_2', '').title()}"
            if poke_data.get("type_2")
            else ""
        )
        + "\n"
        f"[bold]HT:[/bold] {poke_data.get('height_m', '0')}m  |  [bold]WT:[/bold] {poke_data.get('weight_kg', '0')}kg\n"
        f"[bold]Ability:[/bold] {poke_data.get('ability_1', 'None').replace('-', ' ').title()}\n"
        f"[bold]Tier:[/bold] {poke_data.get('stat_tier', 'Unknown')}\n\n"
        "[blue]──────────────────────────────────────────────[/blue]\n\n"  # Smooth horizontal rule
        f"• [bold]HP:[/bold] {get_stat_bar('hp')}\n\n"
        f"• [bold]Attack:[/bold] {get_stat_bar('attack')}\n\n"
        f"• [bold]Defense:[/bold] {get_stat_bar('defense')}\n\n"
        f"• [bold]Sp. Atk:[/bold] {get_stat_bar('sp_attack')}\n\n"
        f"• [bold]Sp. Def:[/bold] {get_stat_bar('sp_defense')}\n\n"
        f"• [bold]Speed:[/bold] {get_stat_bar('speed')}\n\n"
        "[blue]──────────────────────────────────────────────[/blue]\n\n"
        f"[yellow]Description:[/yellow]\n"
        f'[italic]"{poke_data.get("description", "No data available.")}"[/italic]'
    )

    return extra_text


def print_dashboard(img_path: Path | None, info: dict) -> None:
    if img_path is None:
        raise ValueError("argument `img_path` needs to be supplied")

    # Safely extract the pokemon name and data dictionary
    if not info:
        pokemon_name = "Unknown"
        poke_data = {}
    else:
        pokemon_name = info["name"]
        poke_data = cast_to_str(info)

    image_string = generate_image_widget(img_path)

    image_panel = Panel(
        image_string,
        title=f"[green]{pokemon_name.upper()}[/green]",
        expand=False,
    )

    extra_text = extract_extra_text(poke_data)
    data_panel = Panel(extra_text, title="[blue]Pokédex Data[/blue]", expand=True)

    # invisible Rich Table to layout widgets side-by-side
    layout_table = Table.grid(padding=2)  # Slight padding bump for breathing room
    layout_table.add_column(no_wrap=True, max_width=WIDTH)  # Keeps image widget fixed
    layout_table.add_column()

    layout_table.add_row(image_panel, data_panel)

    console.print(layout_table)


def print_comparison(pokemon_a_info: dict, pokemon_b_info: dict) -> None:
    pokemon_a_info = cast_to_str(pokemon_a_info)
    pokemon_b_info = cast_to_str(pokemon_b_info)

    name_a = pokemon_a_info["name"].upper()
    name_b = pokemon_b_info["name"].upper()

    stats = [
        ("HP", "hp"),
        ("Attack", "attack"),
        ("Defense", "defense"),
        ("Sp. Atk", "sp_attack"),
        ("Sp. Def", "sp_defense"),
        ("Speed", "speed"),
    ]

    max_val = 160

    table = Table(
        title=f"[bold]{name_a}[/bold] vs [bold]{name_b}[/bold]",
        expand=False,
    )
    table.add_column("Stat", style="bold", no_wrap=True)
    table.add_column(name_a, no_wrap=True, width=50)
    table.add_column(name_b, no_wrap=True, width=50)

    for stat_name, stat_key in stats:
        val_a = float(pokemon_a_info.get(stat_key, 0))
        val_b = float(pokemon_b_info.get(stat_key, 0))

        ratio_a = min(max(val_a / max_val, 0.0), 1.0)
        ratio_b = min(max(val_b / max_val, 0.0), 1.0)

        bar_a = generate_progress_bar(ratio_a)
        bar_b = generate_progress_bar(ratio_b)

        diff_a = int(val_a - val_b)
        diff_b = int(val_b - val_a)

        if val_a > val_b:
            cell_a = (
                f"{int(val_a)} [green]{bar_a}[/green] [green]({diff_a:+d})[/green]\n"
            )
            cell_b = f"{int(val_b)} [red]{bar_b}[/red] [red]({diff_b:+d})[/red]\n"
        elif val_b > val_a:
            cell_a = f"{int(val_a)} [red]{bar_a}[/red] [red]({diff_a:+d})[/red]\n"
            cell_b = (
                f"{int(val_b)} [green]{bar_b}[/green] [green]({diff_b:+d})[/green]\n"
            )
        else:
            cell_a = f"{int(val_a)} {bar_a} (=)\n"
            cell_b = f"{int(val_b)} {bar_b} (=)\n"

        table.add_row(stat_name, cell_a, cell_b)

    console.print(table)


def print_abilities(abilities: list[dict]) -> None:
    rows_per_col = 60
    num_cols = 6

    table = Table(
        title="[bold]ABILITIES[/bold]",
        expand=False,
    )

    for c in range(num_cols):
        start_id = c * rows_per_col + 1
        end_id = (c + 1) * rows_per_col
        table.add_column(f"[bold]{start_id}-{end_id}[/bold]", no_wrap=True, width=20)

    for r in range(rows_per_col):
        row_cells = []
        for c in range(num_cols):
            idx = c * rows_per_col + r
            if idx < len(abilities):
                entry = abilities[idx]
                row_cells.append(f"{entry['id']} {entry['name']}")
            else:
                row_cells.append("")
        table.add_row(*row_cells)

    console.print(table)


def print_ability_info(ability: dict, have_ability: dict) -> None:
    id = ability.get("id", "???")
    raw_name = ability.get("name", "???")
    name = raw_name.replace("-", " ").title()
    desc = ability.get("description", "???")

    pokemon_names = list(have_ability.values())
    count = len(pokemon_names)

    grid_cols = 3
    pokemon_grid = Table(expand=False, show_header=False, padding=(0, 2))
    for _ in range(grid_cols):
        pokemon_grid.add_column(no_wrap=True)

    for i in range(0, len(pokemon_names), grid_cols):
        chunk = pokemon_names[i : i + grid_cols]
        row = [n.replace("-", " ").title() for n in chunk]
        while len(row) < grid_cols:
            row.append("")
        pokemon_grid.add_row(*row)

    content = Table.grid(padding=(0, 1))
    content.add_column()
    content.add_row(Text.from_markup(f"[italic]{desc}[/italic]"))
    content.add_row(Text(f"\nPokémon with this ability ({count} total):", style="bold"))
    content.add_row(pokemon_grid)

    panel = Panel(
        content,
        title=f"[bold]ABILITY: {id} — {name}[/bold]",
        expand=False,
    )
    console.print(panel)

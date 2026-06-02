import plotext as plt
from rich.markdown import Markdown
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()
WIDTH = 50
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


def print_banner():
    console.print(banner_text)


def get_prompt() -> str:
    text = console.input(PROMPT).strip()
    return text


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
    empty_block = "░"  # You can also use "▒" or a simple space " "

    # Construct the bar
    bar = (full_block * filled_length) + (empty_block * (width - filled_length))

    # Format with percentage
    return f"|{bar}|"


def generate_image_widget(image_path: Path, width: int = WIDTH) -> Text:
    """Generates the high-density Braille string from Plotext."""
    plt.clf()
    plt.plotsize(width, int(width / 2))
    try:
        plt.image_plot(image_path)
        return Text.from_ansi(plt.build())
    except Exception:
        return Text("[red]Image File Not Found[/red]")


def print_dashboard(img_path: Path | None, info: dict = dict()):
    if img_path is None:
        raise ValueError("argument `img_path` needs to be supplied")

    # Safely extract the pokemon name and data dictionary
    if not info:
        pokemon_name = "Unknown"
        poke_data = {}
    else:
        pokemon_name = info["name"]
        poke_data = info
        for key, val in poke_data.items():
            poke_data[key] = str(val)

    image_string = generate_image_widget(img_path, width=WIDTH)

    image_panel = Panel(
        image_string, title=f"[green]{pokemon_name.upper()}[/green]", expand=False
    )

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

    data_panel = Panel(extra_text, title="[blue]Pokédex Data[/blue]", expand=True)

    # invisible Rich Table to layout widgets side-by-side
    layout_table = Table.grid(padding=2)  # Slight padding bump for breathing room
    layout_table.add_column(no_wrap=True)  # Keeps image widget fixed
    layout_table.add_column()

    layout_table.add_row(image_panel, data_panel)

    console.print(layout_table)


def validate_pokedex_info(info: dict) -> tuple[bool, list[str]]:
    """
    Validates that the provided Pokémon info dictionary contains all required fields.

    Returns:
        A tuple of (is_valid, missing_fields)
    """
    # Define the canonical list of fields based on the expected output schema
    REQUIRED_FIELDS = [
        "pokedex_id",
        "genus",
        "generation",
        "type_1",
        "type_2",
        "num_types",
        "hp",
        "attack",
        "defense",
        "sp_attack",
        "sp_defense",
        "speed",
        "base_stat_total",
        "height_m",
        "weight_kg",
        "base_experience",
        "ability_1",
        "ability_2",
        "hidden_ability",
        "color",
        "shape",
        "habitat",
        "growth_rate",
        "egg_groups",
        "is_legendary",
        "is_mythical",
        "is_baby",
        "capture_rate",
        "base_happiness",
        "hatch_counter",
        "gender_rate",
        "description",
        "sprite_url",
        "is_dual_type",
        "bmi",
        "attack_defense_ratio",
        "physical_total",
        "special_total",
        "offensive_total",
        "defensive_total",
        "gender_distribution",
        "stat_tier",
    ]

    # 1. Ensure the dictionary isn't completely empty
    if not info:
        return False, ["Entire dataset is missing or empty"]

    # 2. Extract the inner stats dictionary (e.g., info['charizard'])
    try:
        pokemon_name = list(info.keys())[0]
        poke_data = info[pokemon_name]

        # Ensure poke_data is actually a dictionary
        if not isinstance(poke_data, dict):
            return False, ["Data payload format is invalid (expected a nested dict)"]

    except IndexError, AttributeError:
        return False, ["Invalid dictionary structural format"]

    # 3. Identify any missing fields
    missing_fields = [field for field in REQUIRED_FIELDS if field not in poke_data]

    # 4. Return results
    is_valid = len(missing_fields) == 0
    return is_valid, missing_fields


if __name__ == "__main__":
    print_dashboard(None, {})

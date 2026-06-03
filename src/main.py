import subprocess
import sys
import os
import pandas as pd
from cmdline import (
    print_abilities,
    print_comparison,
    print_dashboard,
    print_banner,
    get_prompt,
    print_ability_info,
    print_type_map,
)
from handlers import display_help
from enum import Enum
from pathlib import Path

BASE_PATH = Path.home() / "pokedex-cli"
CSV_PATH = BASE_PATH / "pokemon-data/pokemon_complete_2025.csv"
ABILITIES_CSV_PATH = BASE_PATH / "pokemon-data/abilities.csv"
TYPE_CHART_CSV_PATH = BASE_PATH / "pokemon-data/pokemon_type_chart.csv"
BASE_IMAGES_PATH = BASE_PATH / "pokemon-images/thumbnails/"

df = pd.read_csv(CSV_PATH)
abilities_df = pd.read_csv(ABILITIES_CSV_PATH)[:311]
type_chart_df = pd.read_csv(TYPE_CHART_CSV_PATH)

pokemon_names = df["name"].to_list()
ABILITIES = abilities_df["name"].to_list()  # type: ignore


class Action(Enum):
    GET_INFO = "/info"
    GET_INFO_BY_ID = "/info-id"
    COMPARE = "/cmp"
    LIST_ALL_ABILITIES = "/abilities"
    GET_ABILITY_INFO = "/ability"
    CLEAR_SCREEN = "/clear"
    TYPE_MATCHUP = "/type-matchup"
    DISPLAY_HELP = "/help"


def repl() -> None:
    while True:
        text = get_prompt()
        if text == "":
            continue
        parts = text.split()
        cmd = parts[0].lower()
        rem = parts[1:]

        match cmd:
            case Action.GET_INFO.value:
                if len(rem) == 0:
                    print("Please specify pokemon(s) name(s)")
                    continue
                invalid_names = {name for name in rem if name not in pokemon_names}
                valid = set(rem) - invalid_names
                if len(valid) == 0:
                    print(f"Invalid names: {invalid_names}")
                    continue
                for name in valid:  # pandas will look for this variable
                    matching_entry = df.query("name == @name")
                    pokemon_info = matching_entry.iloc[0].to_dict()
                    img_path = BASE_IMAGES_PATH / (
                        str(pokemon_info["pokedex_id"]).zfill(4) + ".png"
                    )
                    print_dashboard(img_path.absolute(), pokemon_info)

            case Action.GET_INFO_BY_ID.value:
                if len(rem) == 0:
                    print("Please enter a valid pokemon ID")
                    continue
                try:
                    valid_ids = {
                        id for id in rem if (int(id) > 0) and (int(id) <= 1025)
                    }
                except ValueError as e:
                    print(f"Error: {e}")
                    continue

                invalid = set(rem) - valid_ids

                for id in valid_ids:
                    matching_entry = df.query(f"pokedex_id == {id}")
                    pokemon_info = matching_entry.iloc[0].to_dict()
                    img_path = BASE_IMAGES_PATH / (id.zfill(4) + ".png")
                    print_dashboard(img_path, pokemon_info)

                if invalid:
                    print(f"Invalid IDs: {invalid}")
            case Action.COMPARE.value:
                if len(rem) < 2:
                    print("Please enter two pokemon names")
                    continue
                pokemon_a, pokemon_b = list(map(lambda x: x.lower(), rem[0:2]))
                invalid = [
                    pk for pk in [pokemon_a, pokemon_b] if pk not in pokemon_names
                ]
                if invalid:
                    print(f"Invalid pokemon name(s): {invalid}")
                    continue
                a_info = df.query("name == @pokemon_a").iloc[0].to_dict()
                b_info = df.query("name == @pokemon_b").iloc[0].to_dict()
                print_comparison(a_info, b_info)

            case Action.LIST_ALL_ABILITIES.value:
                abilities = abilities_df[["id", "name"]].to_dict(orient="records")  # type: ignore
                print_abilities(abilities)
            case Action.GET_ABILITY_INFO.value:
                if len(rem) == 0:
                    print("Please specify ability.")
                    continue
                if len(rem) > 1:
                    print("You can only view info for one ability at a time.")
                    continue
                ability = rem[0]
                if ability not in ABILITIES:
                    print(f"Invalid ability: {ability}")
                    continue
                have_ability = df.query(
                    "ability_1 == @ability or ability_2 == @ability or hidden_ability == @ability"
                )["name"].to_dict()

                ability_entry = abilities_df.query("name == @ability").iloc[0].to_dict()
                print_ability_info(ability_entry, have_ability)
            case Action.TYPE_MATCHUP.value:
                print_type_map(type_chart_df)
            case Action.CLEAR_SCREEN.value:
                subprocess.run(["clear"] if os.name == "posix" else ["cls"])
            case Action.DISPLAY_HELP.value:
                display_help()
            case _:
                print(f"Invalid command: {cmd}")


def main() -> None:
    print_banner()
    repl()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)

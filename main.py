import sys
import pandas as pd
from cmdline import (
    print_abilities,
    print_comparison,
    print_dashboard,
    print_banner,
    get_prompt,
    print_ability_info,
)
from enum import Enum
from pathlib import Path

CSV_PATH = "./pokemon_complete_2025.csv"
ABILITIES_CSV_PATH = "./abilities.csv"
BASE_IMAGES_PATH = Path.home() / "pokedex-cli/pokemon-images/thumbnails/"

df = pd.read_csv(CSV_PATH)
abilities_df = pd.read_csv(ABILITIES_CSV_PATH)[:311]

pokemon_names = df["name"].to_list()
ABILITIES = abilities_df["name"].to_list()  # type: ignore


class Action(Enum):
    GET_INFO = "/info"
    GET_INFO_BY_ID = "/info-id"
    COMPARE = "/cmp"
    LIST_ALL_ABILITIES = "/abilities"
    GET_ABILITY_INFO = "/ability"


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
                    print(pokemon_info)
                    img_path = BASE_IMAGES_PATH / (
                        str(pokemon_info["pokedex_id"]).zfill(4) + ".png"
                    )
                    print_dashboard(img_path.absolute(), pokemon_info)

            case Action.GET_INFO_BY_ID.value:
                valid_ids = {id for id in rem if (int(id) > 0) and (int(id) <= 1025)}
                invalid = set(rem) - valid_ids

                for id in valid_ids:
                    matching_entry = df.query(f"pokedex_id == {id}")
                    pokemon_info = matching_entry.iloc[0].to_dict()
                    print(pokemon_info)
                    img_path = BASE_IMAGES_PATH / (id.zfill(4) + ".png")
                    print_dashboard(img_path.absolute(), pokemon_info)

                print(f"Invalid IDs: {invalid}")
            case Action.COMPARE.value:
                if len(rem) != 2:
                    print("You can only compare two pokemons at a time")
                    continue
                pokemon_a, pokemon_b = rem
                a_info = df.query("name == @pokemon_a").iloc[0].to_dict()
                b_info = df.query("name == @pokemon_b").iloc[0].to_dict()
                print_comparison(a_info, b_info)

                print(f"Comparing: {pokemon_a} Vs {pokemon_b}")
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
            case _:
                print(f"Invalid command: {cmd}")


def main():
    print_banner()
    repl()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)

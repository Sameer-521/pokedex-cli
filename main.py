import sys
import pandas as pd
from cmdline import print_comparison, print_dashboard, print_banner, get_prompt
from enum import Enum
from pathlib import Path

CSV_PATH = r"./pokemon_complete_2025.csv"
BASE_IMAGES_PATH = Path.home() / "pokedex-cli/pokemon-images/thumbnails/"

df = pd.read_csv(CSV_PATH)
pokemon_names = df["name"].to_list()


class Action(Enum):
    GET_INFO = "/info"
    GET_INFO_BY_ID = "/info-id"
    COMPARE = "/cmp"


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

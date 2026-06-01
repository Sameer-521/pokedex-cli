import csv
import sys
from helper import print_dashboard, validate_pokedex_info, print_banner, get_prompt
from enum import Enum
from pathlib import Path

CSV_PATH = r"./pokemon_complete_2025.csv"
BASE_IMAGES_PATH = Path.home() / "pokedex-cli/pokemon-images/thumbnails/"


class Action(Enum):
    GET_INFO = "/info"
    GET_INFO_BY_ID = "/info-id"
    COMPARE = "/cmp"


def load_pokemon_data() -> dict:
    data = dict()
    with open(CSV_PATH, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            key = row.pop("name")
            data[key] = row

    return data


def repl() -> None:
    poke_data = load_pokemon_data()
    while True:
        text = get_prompt()
        if text == "":
            continue
        parts = text.split()
        cmd = parts[0].lower()
        rem = parts[1:]

        match cmd:
            case Action.GET_INFO.value:
                info_gotten = []
                invalid_names = []
                for name in rem:
                    entry: dict = poke_data.get(name, {})
                    entry = {name: entry}
                    valid, err = validate_pokedex_info(entry)
                    if valid and not err:
                        info_gotten.append(f"Info: {name}: {entry}")
                        img_path = BASE_IMAGES_PATH / (
                            str(entry[name].get("pokedex_id")).zfill(4) + ".png"
                        )
                        print_dashboard(img_path.absolute(), entry)
                    else:
                        invalid_names.append(f"{name}: {err}")
                print(info_gotten)
                if invalid_names:
                    print(f"Invalid names: {invalid_names}")
            case Action.GET_INFO_BY_ID.value:
                valid_ids = {id for id in rem if (int(id) > 0) and (int(id) <= 1025)}
                invalid = set(rem) - valid_ids

                for item in poke_data:
                    for id in valid_ids:
                        if item.get("pokedex_id", None) == id:
                            pass
            case Action.COMPARE.value:
                if len(rem) != 2:
                    print("You can only compare two pokemons at a time")
                    continue
                pokemon_a, pokemon_b = rem
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

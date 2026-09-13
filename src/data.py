from pathlib import Path

import pandas as pd

BASE_PATH = Path(__file__).resolve().parent.parent

CSV_PATH = BASE_PATH / "pokemon-data/pokemon_complete_2025.csv"
ABILITIES_CSV_PATH = BASE_PATH / "pokemon-data/abilities.csv"
TYPE_CHART_CSV_PATH = BASE_PATH / "pokemon-data/pokemon_type_chart.csv"
EVOLUTIONS_CSV_PATH = BASE_PATH / "pokemon-data/evolutions.csv"
BASE_IMAGES_PATH = BASE_PATH / "pokemon-images/thumbnails/"
SPRITES_AVAILABLE = (BASE_IMAGES_PATH / "0001.png").exists()

df = pd.read_csv(CSV_PATH)
abilities_df = pd.read_csv(ABILITIES_CSV_PATH)
type_chart_df = pd.read_csv(TYPE_CHART_CSV_PATH)

# ids 10001+ are side-game abilities that no pokemon in the dataset has
abilities_df = abilities_df[abilities_df["id"] < 10000]

pokemon_names = set(df["name"].to_list())
ABILITIES = abilities_df["name"].to_list()
MAX_POKEDEX_ID = int(df["pokedex_id"].max())

records: list[dict] = df.to_dict(orient="records")
pokemon_by_name: dict[str, dict] = {pokemon["name"]: pokemon for pokemon in records}
pokemon_by_id: dict[int, dict] = {
    int(pokemon["pokedex_id"]): pokemon for pokemon in records
}

ability_by_name: dict[str, dict] = {
    ability["name"]: ability for ability in abilities_df.to_dict(orient="records")
}

by_type: dict[str, list[dict]] = {}
ability_owners: dict[str, list[str]] = {}
for pokemon in records:
    for pokemon_type in (pokemon["type_1"], pokemon["type_2"]):
        if pd.notna(pokemon_type):
            by_type.setdefault(pokemon_type, []).append(pokemon)
    for ability_column in ("ability_1", "ability_2", "hidden_ability"):
        ability = pokemon[ability_column]
        if pd.notna(ability):
            ability_owners.setdefault(ability, []).append(pokemon["name"])

# evolution edges from the flat csv (one row per edge: evolves_from -> name)
evolutions_df = pd.read_csv(EVOLUTIONS_CSV_PATH)

# form pokemon are dumped under their plain name with a blank pokedex_id
# (e.g. 'eiscue' instead of 'eiscue-ice'); resolve them to dataset names
_alias: dict[str, str] = {}
for plain_name in evolutions_df.loc[
    evolutions_df["pokedex_id"].isna(), "name"
].unique():
    matches = [
        dataset_name
        for dataset_name in pokemon_names
        if dataset_name.startswith(plain_name + "-")
    ]
    if len(matches) == 1:
        _alias[plain_name] = matches[0]

evolves_to: dict[str, list[tuple[str, str]]] = {}
evolves_from: dict[str, tuple[str, str]] = {}
for row in evolutions_df.itertuples(index=False):
    if pd.isna(row.evolves_from):
        continue
    source = _alias.get(str(row.evolves_from), str(row.evolves_from))
    target = _alias.get(str(row.name), str(row.name))
    if pd.notna(row.evolution_condition):
        condition = row.evolution_condition
    elif pd.notna(row.evolution_trigger):
        condition = row.evolution_trigger
    else:
        condition = ""
    evolves_to.setdefault(source, []).append((target, condition))
    evolves_from[target] = (source, condition)

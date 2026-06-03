# Pokédex CLI

A terminal-based Pokédex built with Python and Rich. Explore 1025 Pokémon with sprite rendering, stat visualizations, type charts, and more — all from your command line.

> **Important:** This version uses `rich-pixels` for sprite rendering and side-by-side dashboard layouts. Small terminal windows are not supported. Run in **full-screen mode** for the best experience.

## Finished Features

- **`/info <name...>`** — Full dashboard for one or more Pokémon by name. Shows sprite, stats with progress bars, type, height/weight, abilities, and dex description.
- **`/info-id <id...>`** — Same as `/info`, but by Pokédex ID (1–1025).
- **`/cmp <a> <b>`** — Side-by-side stat comparison with color-coded progress bars and diff annotations (green for winner, red for loser).
- **`/abilities`** — Paginated 6-column table listing all 311 abilities with their IDs.
- **`/ability <name>`** — Ability description plus a grid of all Pokémon that have the ability.
- **`/type-matchup`** — Full 18×18 type effectiveness heatmap with colored blocks and a type/legend key.
- **`/clear`** — Clears the terminal screen.
- **`/help`** — Displays all available commands.

## Setup

```bash
uv sync
uv run main.py
```

Requires **Python 3.14+**.

## Data

- `pokemon-data/pokemon_complete_2025.csv` — 1025 Pokémon with stats, types, abilities, and descriptions
- `pokemon-data/abilities.csv` — 372 abilities with flavor text
- `pokemon-data/pokemon_type_chart.csv` — Full 18×18 type effectiveness matrix
- `pokemon-images/thumbnails/` — Sprite PNGs rendered in-terminal via `rich-pixels`

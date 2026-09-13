import sys
from enum import Enum

from cmdline import console, get_prompt, print_banner
from data import SPRITES_AVAILABLE
from handlers import (
    display_help,
    handle_abilities,
    handle_ability,
    handle_cmp,
    handle_evo,
    handle_info,
    handle_info_by_id,
    handle_list,
    handle_type_matchup,
)


class Action(Enum):
    GET_INFO = "/info"
    GET_INFO_BY_ID = "/info-id"
    COMPARE = "/cmp"
    LIST_ALL_ABILITIES = "/abilities"
    GET_ABILITY_INFO = "/ability"
    CLEAR_SCREEN = "/clear"
    TYPE_MATCHUP = "/type-matchup"
    DISPLAY_HELP = "/help"
    GET_EVOLUTION = "/evo"
    LIST_TYPE = "/list"
    EXIT = "/exit"
    QUIT = "/quit"


def repl() -> None:
    while True:
        text = get_prompt()
        if text == "":
            continue
        parts = text.split()
        cmd = parts[0].lower()
        args = parts[1:]

        match cmd:
            case Action.GET_INFO.value:
                handle_info(args)
            case Action.GET_INFO_BY_ID.value:
                handle_info_by_id(args)
            case Action.COMPARE.value:
                handle_cmp(args)
            case Action.LIST_ALL_ABILITIES.value:
                handle_abilities()
            case Action.GET_ABILITY_INFO.value:
                handle_ability(args)
            case Action.TYPE_MATCHUP.value:
                handle_type_matchup()
            case Action.CLEAR_SCREEN.value:
                print("\033[2J\033[H", end="")
            case Action.DISPLAY_HELP.value:
                display_help()
            case Action.GET_EVOLUTION.value:
                handle_evo(args)
            case Action.LIST_TYPE.value:
                handle_list(args)
            case Action.EXIT.value | Action.QUIT.value:
                break
            case _:
                print(f"Invalid command: {cmd}")


def main() -> None:
    print_banner()
    if not SPRITES_AVAILABLE:
        console.print(
            "[yellow]Sprites not found. Run 'uv run init.py' to extract them.[/yellow]"
        )
    repl()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)

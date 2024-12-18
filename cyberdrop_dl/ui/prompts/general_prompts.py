from __future__ import annotations

import asyncio
import os
import pathlib
from typing import TYPE_CHECKING

from InquirerPy import inquirer, get_style
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from InquirerPy.validator import EmptyInputValidator, PathValidator
from rich.console import Console

from cyberdrop_dl.utils.transfer.transfer_v4_config import transfer_v4_config
from cyberdrop_dl.utils.transfer.transfer_v4_db import transfer_v4_db
from cyberdrop_dl.utils.utilities import log

if TYPE_CHECKING:
    from typing import List

    from cyberdrop_dl.managers.manager import Manager

console = Console()


def main_prompt(manager: Manager) -> int:
    """Main prompt for the program"""
    choices = [
        Choice(1, "Download"),
        Choice(2, "Download (All Configs)"),
        Choice(3, "Retry Failed Downloads"),
        Choice(4, "Create File Hashes"),
        Choice(5, "Sort All Configs"),
        Choice(6, "Edit URLs"),
        Separator(),
        Choice(7, f"Select Config (Current: {manager.config_manager.loaded_config})"),
        Choice(8, "Change URLs.txt file and Download Location"),
        Choice(9, "Edit Configs"),
        Separator(),
        Choice(10, "Check for Updates"),
        Choice(11, "Import Cyberdrop_V4 Items"),
        Choice(12, "View Changelog"),
        Choice(13, "Exit"),
    ]

    simp_disclaimer_shown = manager.cache_manager.get("simp_disclaimer_shown")
    if simp_disclaimer_shown == None:
        choices = [Choice(-1, "!! VIEW DISCLAIMER !!")]

    action = inquirer.select(
        message="What would you like to do?",
        choices=choices, long_instruction="ARROW KEYS: Navigate | ENTER: Select",
        style=get_style({"pointer": "#ff0000 bold"}) if simp_disclaimer_shown == None else None,
        vi_mode=manager.vi_mode,
    ).execute()

    return action


def manage_configs_prompt(manager: Manager) -> int:
    """Manage Configs Prompt"""
    console.clear()
    action = inquirer.select(
        message="What would you like to do?",
        choices=[
            Choice(1, "Change Default Config"),
            Choice(2, "Create A New Config"),
            Choice(3, "Delete A Config"),
            Separator(),
            Choice(4, "Edit Config"),
            Choice(5, "Edit Authentication Values"),
            Choice(6, "Edit Global Values"),
            Choice(7, "Done"),
        ], long_instruction="ARROW KEYS: Navigate | ENTER: Select",
        vi_mode=manager.vi_mode,
    ).execute()

    return action


def select_config_prompt(manager: Manager, configs: List) -> str:
    """Select a config file from a list of configs"""
    choice = inquirer.fuzzy(
        choices=configs,
        multiselect=False,
        validate=lambda result: len(result) > 0,
        invalid_message="Need to select a config.",
        message="Select a config file:",
        long_instruction="ARROW KEYS: Navigate | TYPE: Filter | TAB: select, ENTER: Finish Selection",
        vi_mode=manager.vi_mode,
    ).execute()

    return choice


def import_cyberdrop_v4_items_prompt(manager: Manager) -> None:
    """Import Cyberdrop_V4 Items"""
    while True:
        console.clear()
        console.print("Editing Config Values")
        action = inquirer.select(
            message="What would you like to do?",
            choices=[
                Choice(1, "Import Config"),
                Choice(2, "Import download_history.sql"),
                Choice(3, "Done"),
            ], long_instruction="ARROW KEYS: Navigate | ENTER: Select",
            vi_mode=manager.vi_mode,
        ).execute()

        # Import Config
        if action == 1:
            new_config_name = inquirer.text(
                message="What should this config be called?",
                validate=EmptyInputValidator("Input should not be empty"),
                vi_mode=manager.vi_mode,
            ).execute()

            if (manager.path_manager.config_dir / new_config_name).is_dir():
                console.print(f"Config with name '{new_config_name}' already exists!")
                inquirer.confirm(message="Press enter to return to the import menu.").execute()
                continue

            home_path = "~/" if os.name == "posix" else "C:\\"
            import_config_path = inquirer.filepath(
                message="Select the config file to import",
                default=home_path,
                validate=PathValidator(is_file=True, message="Input is not a file"),
            ).execute()

            transfer_v4_config(manager, import_config_path, new_config_name)

        # Import download_history.sql
        elif action == 2:
            home_path = "~/" if os.name == "posix" else "C:\\"
            import_download_history_path = inquirer.filepath(
                message="Select the download_history.sql file to import",
                default=home_path,
                validate=PathValidator(message="Input is not a file"),
                vi_mode=manager.vi_mode,
                filter=lambda x: pathlib.Path(x)
            ).execute()
            if import_download_history_path.is_file():
                transfer_v4_db(import_download_history_path, manager.path_manager.history_db)
            else:
                loop = asyncio.new_event_loop()
                for ele in pathlib.Path(import_download_history_path).glob("**/*.sqlite"):
                    if str(ele) == str(manager.path_manager.history_db):
                        continue
                    try:
                        transfer_v4_db(ele, manager.path_manager.history_db)
                    except Exception as e:
                        loop.run_until_complete(log(f"Error importing {ele.name}: {str(e)}", 20))

        # Done
        elif action == 3:
            break


def donations_prompt(manager: Manager) -> None:
    """Donations prompt"""
    console.clear()
    console.print("[bold]Donations[/bold]")
    console.print("")
    console.print("I started making this program around three years ago at this point,"
                "\nIt has grown larger than I could've imagined and I'm very proud of it."
                "\nI have put a lot of time and effort into this program and I'm glad that people are using it."
                "\nThanks to everyone that have supported me, "
                "it keeps me motivated to continue working on this program.")
    console.print("")
    console.print("If you'd like to support me and my work, you can donate to me via the following methods:")
    console.print("BuyMeACoffee: https://www.buymeacoffee.com/jbsparrow")
    console.print("Github Sponsor: https://github.com/sponsors/jbsparrow")

    console.print("")
    console.print("Thank you for your support!")
    console.print("")
    inquirer.confirm(message="Press enter to return to the main menu.", vi_mode=manager.vi_mode).execute()

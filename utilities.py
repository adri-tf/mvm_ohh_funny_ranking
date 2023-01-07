"""archives.py"""
from lxml import html
import os
from typing import List, Callable

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

CONSOLE_DUMP_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\Team Fortress 2\tf"
MVM_RANKING_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\Team Fortress 2\tf\cfg\mvm_ranking.cfg"
STEAM_ID_FINDER_XPATH = "//tr/td/code/text()"

OPTIONS = Options()
OPTIONS.headless = True  # False: Firefox window will show up
OPTIONS.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'


class PlayerData:
    """Data of a player"""

    def __init__(self, username: str, steamid3: str):
        self.username: str = username
        self.steamid3: str = steamid3
        self.steamid64: str = ""
        self.progress: int = -1


def get_players_id(folder_path) -> (List[PlayerData], list):
    """Retrieve the steamID64 of the players from the console dump file.

    :param folder_path: path tp the console dump file.
    """
    files_to_delete: list = []
    max_n, con_dump_path = -1, ""
    for file_name in os.listdir(folder_path):
        if file_name[:7] == "condump" and file_name[-4:] == ".txt":
            if int(file_name[7:-4]) > max_n:
                max_n = int(file_name[7:-4])
                con_dump_path = os.path.join(CONSOLE_DUMP_PATH, file_name)
                files_to_delete.append(os.path.join(folder_path, file_name))

    if max_n < 0:
        print("No console dump file found")
        input()
        exit()

    data: List[PlayerData] = []
    with open(con_dump_path, encoding='utf8') as file:
        for line in file:
            if "[U:1" in line:  # steamID is: [U:1:STEAM_ID]
                username = line.split('"')[1]  # username is right after the first "
                steamid3 = "[U:1" + line.split("[U:1")[-1][:11]
                data.append(PlayerData(username, steamid3))
    print(f"condump{max_n}.txt file data retrieved")

    # SteamID64
    for player_data in data:
        page = requests.get("https://steamidfinder.com/lookup/" + player_data.steamid3)
        tree = html.fromstring(page.content)
        player_data.steamid64 = tree.xpath(STEAM_ID_FINDER_XPATH)[2]
    return data, files_to_delete


def get_players_data(data: List[PlayerData], url: str, xpath: str) -> List[PlayerData]:
    """Retrieve the data of the players by their steamID64.

    :param data: list of players data
    :param url: url of the website to scrap
    :param xpath: xpath to the html box desired
    """
    print("Retrieving players data...")
    driver = webdriver.Firefox(options=OPTIONS, service=Service('./browser/geckodriver.exe'))
    for player_data in data:
        driver.get(url + player_data.steamid64)
        try:
            WebDriverWait(driver, 6).until(
                ec.visibility_of_element_located((By.XPATH, xpath)))
            result = driver.find_element('xpath', xpath).text
            player_data.progress = int(result.split()[2])
        except TimeoutException:
            player_data.progress = 0
        print(player_data.progress, "\t", player_data.steamid64, "\t", player_data.username)
    driver.quit()
    return data


def remove_con_dump_files(files_to_delete: list):
    """Remove all console dump files."""
    print("Press Enter to delete file...")
    input()
    for file_path in files_to_delete:
        os.remove(file_path)


def main(url: str, xpath: str, create_cfg_file: Callable):
    """Main function."""
    players_data, con_dump_files = get_players_id(CONSOLE_DUMP_PATH)
    get_players_data(players_data, url, xpath)
    create_cfg_file(players_data)
    remove_con_dump_files(con_dump_files)

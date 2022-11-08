"""archives.py"""
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

CONSOLE_SCREEN_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\Team Fortress 2\tf\condump000.txt"
MVM_RANKING_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\Team Fortress 2\tf\cfg\mvm_ranking.cfg"

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


def get_players_id(path) -> List[PlayerData]:
    """Retrieve the steamID64 of the players from the console dump file.

    :param path: path tp the console dump file.
    """
    if not os.path.exists(path):
        print("condump000.txt file does not exist")
        input()
        exit()

    data: List[PlayerData] = []
    with open(path, encoding='utf8') as file:
        for line in file:
            if "[U:1" in line:  # steamID is: [U:1:STEAM_ID]
                username = line.split('"')[1]  # username is right after the first "
                steamid3 = "[U:1" + line.split("[U:1")[-1][:11]
                data.append(PlayerData(username, steamid3))
    print("Console dump file data retrieved")

    # SteamID64
    for player_data in data:
        req = requests.get("https://steamidfinder.com/lookup/" + player_data.steamid3)
        soup = BeautifulSoup(req.content, features="html.parser")
        player_data.steamid64 = str(soup.find_all('a', text='Add to Friends')[0])[53:-36]
    return data


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
    driver.close()
    print("Players data retrieved")
    return data


def main(url: str, xpath: str, create_cfg_file: Callable):
    """Main function."""
    players_data = get_players_id(CONSOLE_SCREEN_PATH)
    get_players_data(players_data, url, xpath)
    create_cfg_file(players_data)
    print("Press Enter to delete file...")
    input()
    os.remove(CONSOLE_SCREEN_PATH)

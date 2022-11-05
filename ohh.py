"""ohh.py"""
import os
from typing import List

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

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


def get_con_dump_info(path) -> List[PlayerData]:
    """Retrieve the all the usernames and steamID3 of the players from the console dump file."""
    if not os.path.exists(path):
        print("condump000.txt file does not exist")
        input()
        exit()

    data: List[PlayerData] = []
    with open(path, encoding='utf8') as file:
        for line in file:
            if "[U:1" in line:  # steam_ID is: [U:1:STEAM_ID]
                username = line.split('"')[1]  # username is right after the first "
                steamid3 = "[U:1" + line.split("[U:1")[-1][:11]
                data.append(PlayerData(username, steamid3))
    print("Console dump file data retrieved")
    return data


def get_all_steamid64(data: List[PlayerData]) -> List[PlayerData]:
    """Retrieve the steamID64 from a list of steamID3"""
    print("Retrieving players data...")
    driver = webdriver.Firefox(options=OPTIONS, service=Service('./browser/geckodriver.exe'))
    for player_data in data:
        # SteamID64
        req = requests.get("https://steamidfinder.com/lookup/" + player_data.steamid3)
        soup = BeautifulSoup(req.content, features="html.parser")
        player_data.steamid64 = str(soup.find_all('a', text='Add to Friends')[0])[53:-36]

        # Player progress
        driver.get("https://potato.tf/progress/" + player_data.steamid64)
        WebDriverWait(driver, 10).until(
            ec.visibility_of_element_located((By.XPATH, "//p[@id='wave-progressbar-text']")))
        result = driver.find_element('xpath', '//p[@id="wave-progressbar-text"]').text
        player_data.progress = int(result.split()[2])
        print(player_data.progress, "\t", player_data.username)

    driver.close()
    print("Players data retrieved")
    return players_data


def create_cfg_file(data: List[PlayerData]):
    """Cfg file creation."""
    mvm_ranking_file = open(MVM_RANKING_PATH, 'w', encoding='utf8')
    event = "Operation Holographic Harvest"

    for i, p_d in enumerate(data):
        if p_d.progress == 0:
            mvm_ranking_file.write("alias p" + str(i + 1) + " say \"beep boop, noob spotted: "
                                   + p_d.username + " with ZERO mission completed!\"\n")
        elif p_d.progress == 1:
            mvm_ranking_file.write("alias p" + str(i + 1) + " say \"beep boop, noob spotted: "
                                   + p_d.username + " with only 1 mission completed!\"\n")
        elif p_d.progress < 6:
            mvm_ranking_file.write("alias p" + str(i + 1) + " say \"beep boop, noob spotted: "
                                   + p_d.username + " with only " + str(p_d.progress) + " missions completed!\"\n")
        elif p_d.progress < 11:
            mvm_ranking_file.write("alias p" + str(i + 1) + " say \"" + p_d.username + " is an Amateur of " + event +
                                   " with " + str(p_d.progress) + " missions completed!\"\n")
        elif p_d.progress < 16:
            mvm_ranking_file.write("alias p" + str(i + 1) + " say \"" + p_d.username + " is a Master of " + event +
                                   " with " + str(p_d.progress) + " missions completed!\"\n")
        elif p_d.progress < 21:
            mvm_ranking_file.write("alias p" + str(i + 1) + " say \"" + p_d.username + " is a Pro of " + event +
                                   " with " + str(p_d.progress) + " missions completed!\"\n")
        elif p_d.progress < 26:
            mvm_ranking_file.write("alias p" + str(i + 1) + " say \"" + p_d.username + " is an Expert of " + event +
                                   " with " + str(p_d.progress) + " missions completed!\"\n")
        elif p_d.progress < 32:
            mvm_ranking_file.write("alias p" + str(i + 1) + " say \"" + p_d.username + " is a Veteran of " + event +
                                   " with " + str(p_d.progress) + " missions completed!\"\n")
        elif p_d.progress == 32:
            mvm_ranking_file.write("alias p" + str(i + 1) + " say \"" + p_d.username + " is a God of " + event +
                                   " with all " + str(p_d.progress) + " missions completed!\"\n")
        else:
            print(f"{p_d.progress} points has no associated sentence")
        mvm_ranking_file.write("echo \"p" + str(i + 1) + " with " + str(p_d.progress)
                               + ' stars' + " is " + p_d.username + "\"\n\n")
    mvm_ranking_file.close()
    print("Cfg file created")


if __name__ == "__main__":
    players_data = get_con_dump_info(CONSOLE_SCREEN_PATH)
    get_all_steamid64(players_data)
    create_cfg_file(players_data)
    print("Press Enter to delete file...")
    input()
    os.remove(CONSOLE_SCREEN_PATH)

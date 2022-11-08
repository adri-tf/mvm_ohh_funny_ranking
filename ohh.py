"""ohh.py"""
from typing import List

from utilities import PlayerData, MVM_RANKING_PATH, main


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
        elif p_d.progress < 12:
            mvm_ranking_file.write("alias p" + str(i + 1) + " say \"" + p_d.username + " is an Amateur of " + event +
                                   " with " + str(p_d.progress) + " missions completed!\"\n")
        elif p_d.progress < 18:
            mvm_ranking_file.write("alias p" + str(i + 1) + " say \"" + p_d.username + " is a Master of " + event +
                                   " with " + str(p_d.progress) + " missions completed!\"\n")
        elif p_d.progress < 23:
            mvm_ranking_file.write("alias p" + str(i + 1) + " say \"" + p_d.username + " is a Pro of " + event +
                                   " with " + str(p_d.progress) + " missions completed!\"\n")
        elif p_d.progress < 28:
            mvm_ranking_file.write("alias p" + str(i + 1) + " say \"" + p_d.username + " is an Expert of " + event +
                                   " with " + str(p_d.progress) + " missions completed!\"\n")
        elif p_d.progress < 33:
            mvm_ranking_file.write("alias p" + str(i + 1) + " say \"" + p_d.username + " is a Veteran of " + event +
                                   " with " + str(p_d.progress) + " missions completed!\"\n")
        elif p_d.progress == 33:
            mvm_ranking_file.write("alias p" + str(i + 1) + " say \"" + p_d.username + " is a God of " + event +
                                   " with all " + str(p_d.progress) + " missions completed!\"\n")
        else:
            print(f"{p_d.progress} points has no associated sentence")
            mvm_ranking_file.write("echo \"p" + str(i + 1) + " ERROR: " + str(p_d.progress)
                                   + " missions has no associated sentence is " + p_d.username + "\"\n\n")
            continue
        mvm_ranking_file.write("echo \"p" + str(i + 1) + " with " + str(p_d.progress)
                               + " missions is " + p_d.username + "\"\n\n")
    mvm_ranking_file.close()
    print("Cfg file created")


URL = "https://potato.tf/progress/"
XPATH = "//p[@id='wave-progressbar-text']"

if __name__ == "__main__":
    main(URL, XPATH, create_cfg_file)

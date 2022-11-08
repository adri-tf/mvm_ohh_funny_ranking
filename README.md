# mvm_funny_ranking
Join a server and judge people about their score in Operation Holographic Harvest.

Protocol :
- get user Steam ID ;
- find the user's html dedicated page ;
- select the data ;
- create a file in your TF2 cfg folder with the information you want to disp.

TF2 Commands :
- 'clear' (clear console) ;
- 'status' (shows all player's id in server) ;
- 'condump' (screenshot of the console saved as condump000.txt).
- after executing the python program : 'exec mvm_ranking'.

## TODO
Instead of only accepting condump000.txt, look for the latest condump by cheecking the number at the end of the file name.
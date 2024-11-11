#! /usr/bin/bash

PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin 
sleep 10  # Gives the network time to initialize

# updates whenever availaible
cd /home/sp/code/backend
git pull
cd /home/sp/code/scripts
git pull

#Backup old files
cd /home/sp/log
cp pycap.log pycap.log.bak
cp spboot.log spboot.log.bak

cd /home/sp
python3 -u /home/sp/code/scripts/starter.py > /home/sp/log/pycap.log &
java -jar /home/sp/code/backend/backend-0.0.1-SNAPSHOT.jar > /home/sp/log/spboot.log &

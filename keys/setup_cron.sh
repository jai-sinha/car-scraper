#!/bin/bash

# this should add a cron job to clear the api call count every day at midnight
# it should also remove any duplicate cron jobs
PATH_TO_SCRIPT=$(pwd)/reset_count.sh

(crontab -l; echo "0 0 * * * $PATH_TO_SCRIPT")|awk '!x[$0]++'|crontab -

echo "------------------------------------------------------------"
echo "cron job added to run reset_count.sh at midnight every day"
echo "use 'crontab -l' to confirm it's been added correctly"
echo "------------------------------------------------------------"
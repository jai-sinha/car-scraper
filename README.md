# README

## Overview:

This project is intended as a tool to make searching for a specific cool car easier! It should not be used for (or take away) the timeless joy of randomly browsing cool cars. But basically with (sort of) one click, it pulls and outputs results from a number of commonly-used websites, saving its user from the repetitive task of cross-checking the same make/model/year/etc over and over while searching for the right one to buy.

## API Instructions:
Get your free Google API Key [here](https://developers.google.com/custom-search/v1/overview), and add it to keys/keys.json under "google". Then, in the keys directory, run ./setup_cron.sh to automate resetting the api use count daily. View today's use count at any time in `keys/api_uses.txt`.
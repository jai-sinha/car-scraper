# README

## Overview:

This project is intended as a tool to make searching for a specific cool car easier! It should not be used for (or take away) the timeless joy of randomly browsing cool cars. But basically with (sort of) one click, it pulls and outputs results from a number of commonly-used websites, saving the user from the repetitive task of cross-checking the same make/model/year/etc over and over while searching for the right one to buy.

## Instructions:
First, get your free Google API Key [here](https://developers.google.com/custom-search/v1/overview), and add it to `scraper/keys/keys.json` under `"google"`.

Then, create a virtual environment in the `scraper` directory with `python3 -m venv .venv`. Start it with `source .venv/bin/activate`, and run `pip3 install -r requirements.txt`. Go into the `src` directory, and run `python3 main.py`. Your server should be up and running!

Lastly, to get the site up, go back into the main `car-scraper` directory, and then into `/site`. Make sure you have npm installed, and run `npm install` and `npm run dev`. The second command should give you a clickable link to localhost:5173, which will take you to your Car Scraper!

Enjoy :)
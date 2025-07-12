# README

## Overview:

This project is intended as a tool to make searching for a specific cool car easier! It should not be used for (or take away from) the timeless joy of randomly browsing cool cars. But basically with (sort of) one click, it pulls and outputs results from a number of commonly-used websites, saving you from the unending task of repeatedly cross-checking the same make/model/year/etc while searching for the right one to buy.

## Getting Started:

1. Clone the repository by running `git clone https://github.com/yourusername/car-scraper.git` in your desired destination directory. Enter the folder with `cd car-scraper`. 
2. Follow the instructions in .env.example to set up environment variables for the API calls and database secrets. 
3. Install Docker (if you don't already have it), either by going [here](https://www.docker.com/products/docker-desktop/) or running `brew install --cask docker`. Login to your account on the via `docker login -u *your username*` or by opening the desktop app. 
4. Run `docker compose up --build -d` in the project root directory, or `docker compose up -d` for subsequent runs after initial build. 
5. Use the scraper UI by navigating to http://localhost:5173 in your browser, or make API calls directly at http://127.0.0.1:5001/. A detailed API description can be found in `openapi.yaml`.

## Notes:

- The Docker app has a useful UI for checking container logs and CPU usage. The scheduler container can be pretty resource-heavy, but it is necessary to keep the database updated with live auction info and to populate the DB with listing info necessary for using DB search instead of scrape search. `.env.example` has instructions on how to slow it down if needed.

- Once logged in, you can click the star icon on a listing to save it to your garage. Click again to unsave it.

- Yeah there's not any point in using an email to register/login at the moment, but who knows– maybe someday it'll be useful, and I don't feel like removing it at the moment.

- Result filtering is currently not an option when making API calls directly, it's a frontend only feature.
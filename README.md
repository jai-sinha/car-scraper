# README

## Overview:

This project is intended as a tool to make searching for a specific cool car easier! It should not be used for (or take away from) the timeless joy of randomly browsing cool cars. But basically with (sort of) one click, it pulls and outputs results from a number of commonly-used websites, saving you from the unending task of repeatedly cross-checking the same make/model/year/etc while searching for the right one to buy.

## Developer Instructions:

First, make sure you have Docker installed, either by going [here](https://www.docker.com/products/docker-desktop/) or via `brew install --cask docker`. Then, login to your account on the CLI (via `docker login -u *your username*`) or the desktop app. Once logged in, run `docker compose up --build` in the project root directory, or `docker compose up -d` for subsequent runs after initial build. Use the scraper by opening http://localhost:5173 in your browser, or making API calls at http://127.0.0.1:5001/.
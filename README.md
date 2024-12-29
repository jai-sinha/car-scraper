# README

## Overview:

This project is intended as a tool to make searching for a specific cool car easier! It should not be used for (or take away) the timeless joy of randomly browsing cool cars. But basically with (sort of) one click, it pulls and outputs results from a number of commonly-used websites, saving its user from the repetitive task of cross-checking the same make/model/year/etc over and over while searching for the right one to buy.

## Goals (in some order, kinda):

- ***Do not get bored and quit***
- Add custom searches instead of hardcoding 991 911s
- Add a UI of sorts, or just a CLI
- Add support for **eBay**, **Cars.com**, **CarGurus**, and **AutoTrader**. *Note: this may never happen because I don't really like them or their interfaces*


## Possible ways to scale up in the very distant future, or really just cool ideas that technically could become reality, but probably won't:

- Make a good UI, like with React or Django or something
- Add user DBs, so you can bookmark a car, or remove it from any future searches
- Take the data and make predictions about future prices

## Known Issues:
- It's very fragile, searching needs to be very precise and search terms vary heavily between even just the three sites I have running
- No clean way of handling the variation arising just from the three sites (e.g. subtitles with c&b, dt with pcar)
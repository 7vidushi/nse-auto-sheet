# NSE Volume Breakout Google Sheet Automation

## Project Overview

This project is an automated Google Sheet system for NSE stock data screening. It automatically fetches the latest available NSE bhavcopy data, filters equity stocks, sorts them by trading volume, and updates a Google Sheet with the top 250 highest-volume NSE stocks.

The project is based on the first stage of a volume breakout stock screener. At the current stage, the system updates the Google Sheet with basic stock data such as NSE Code, Volume, and Close Price. Further breakout analysis using 50 DMA, 100 DMA, 200 DMA, CAR, and final filtering will be added later.

## Current Status

The current system successfully performs the following tasks:

1. Fetches the latest available NSE bhavcopy data.
2. Filters normal equity stocks.
3. Removes non-equity instruments such as ETFs, liquid funds, gold, silver, bonds, and other similar securities.
4. Sorts stocks based on trading volume.
5. Selects the top 250 highest-volume NSE stocks.
6. Updates the Google Sheet automatically.
7. Shows the last updated time and bhavcopy date.

## Google Sheet Structure

The Google Sheet is named:

```text
Volume Breakout

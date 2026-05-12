# Setup Guide: NSE Volume Breakout Google Sheet Automation

## Purpose of This Guide

This guide explains how to recreate the NSE Volume Breakout Google Sheet Automation project from the beginning.

The purpose of this project is to automatically fetch NSE bhavcopy data, filter equity stocks, sort them by volume, select the top 250 highest-volume stocks, and update a Google Sheet.

At the current stage, this project works as an automated NSE volume-data updater. Further breakout analysis using 50 DMA, 100 DMA, 200 DMA, CAR, and final breakout filtering will be added later.

---

## Step 1: Create the Google Sheet

1. Open Google Drive.
2. Click **New**.
3. Select **Google Sheets**.
4. Rename the spreadsheet as:

```text
Volume Breakout
```

5. Create two tabs inside the Google Sheet:

```text
Top 250 Stocks
Final List
```

6. In the **Top 250 Stocks** tab, add the following headings:

| Cell | Heading |
|---|---|
| A1 | NSE Code |
| B1 | Volume |
| C1 | Close Price |

The Python automation will later update the stock data from row 2 onward.

---

## Step 2: Create a Google Cloud Project

1. Open Google Cloud Console.
2. Create a new project.
3. Name the project:

```text
Volume Breakout Bot
```

4. Make sure this project is selected before continuing.

Google Cloud Console is used to give permission to the Python automation so that it can update the Google Sheet.

---

## Step 3: Enable Required APIs

Inside Google Cloud Console, enable the following APIs:

1. **Google Sheets API**
2. **Google Drive API**

These APIs allow the Python script to access and update the Google Sheet.

---

## Step 4: Create a Service Account

1. Go to **IAM & Admin**.
2. Open **Service Accounts**.
3. Create a new service account.
4. Name it:

```text
Stock Updater Bot
```

5. After creating it, copy the service account email.

The service account works like a robot email ID. This robot account will be used by the Python script to update the Google Sheet.

---

## Step 5: Download the JSON Key

1. Open the service account.
2. Go to the **Keys** tab.
3. Click **Add Key**.
4. Select **Create New Key**.
5. Choose **JSON**.
6. Download the JSON key file.

Important: Do not share this JSON file publicly. It works like a private access key for the service account.

---

## Step 6: Share the Google Sheet with the Service Account

1. Open the Google Sheet named **Volume Breakout**.
2. Click **Share**.
3. Paste the service account email.
4. Give it **Editor** access.
5. Click **Send** or **Share**.

This step is necessary because the service account must have permission to edit the Google Sheet.

---

## Step 7: Get the Spreadsheet ID

Open the Google Sheet URL.

Example:

```text
https://docs.google.com/spreadsheets/d/SPREADSHEET_ID_HERE/edit
```

Copy only the part between:

```text
/d/
```

and:

```text
/edit
```

This copied part is called the **Spreadsheet ID**.

The Python script uses this ID to know which Google Sheet to update.

---

## Step 8: Create a GitHub Repository

1. Open GitHub.
2. Create a new repository.
3. Keep the repository **Private**.
4. Suggested repository name:

```text
nse-auto-sheet
```

The GitHub repository stores the Python automation code and workflow file.

---

## Step 9: Add GitHub Secrets

Go to:

```text
Repository Settings → Secrets and variables → Actions
```

Add two repository secrets:

### 1. GCP_CREDENTIALS

Open the downloaded JSON key file in Notepad.

Copy the full content and paste it as the value for:

```text
GCP_CREDENTIALS
```

### 2. SPREADSHEET_ID

Paste the Google Sheet ID as the value for:

```text
SPREADSHEET_ID
```

Important: These secrets should never be shared publicly.

---

## Step 10: Add Project Files

The repository should contain these files:

```text
requirements.txt
updatesheet.py
.github/workflows/update-sheet.yml
README.md
SETUP_GUIDE.md
```

---

## File 1: requirements.txt

This file contains the Python packages required to run the project.

```text
gspread
google-auth
pandas
requests
```

---

## File 2: updatesheet.py

This is the main Python script.

It performs the following tasks:

1. Fetches the latest available NSE bhavcopy data.
2. Reads the zipped CSV file.
3. Filters normal equity stocks.
4. Removes non-equity instruments such as ETFs, liquid funds, gold, silver, cash, bonds, and other securities.
5. Sorts stocks by trading volume.
6. Selects the top 250 highest-volume stocks.
7. Updates the Google Sheet with:
   - NSE Code
   - Volume
   - Close Price
   - Last Updated time
   - Bhavcopy Date

---

## File 3: .github/workflows/update-sheet.yml

This is the GitHub Actions workflow file.

It tells GitHub to run the Python script automatically.

The workflow can run in two ways:

1. **Automatically** on a fixed schedule.
2. **Manually** using the **Run workflow** button in the GitHub Actions tab.

The automation is scheduled to run after market hours so that the latest NSE bhavcopy data can be used.

---

## Step 11: Run the Workflow Manually

To test whether the automation works:

1. Go to the GitHub repository.
2. Open the **Actions** tab.
3. Select the workflow named:

```text
Update NSE Stocks to Google Sheets
```

4. Click **Run workflow**.
5. Wait for the workflow to complete.

If the workflow shows a green tick, it means the automation ran successfully.

---

## Step 12: Check the Google Sheet Output

Open the Google Sheet and go to the **Top 250 Stocks** tab.

The sheet should show:

| Column | Meaning |
|---|---|
| NSE Code | Stock symbol |
| Volume | Number of shares traded |
| Close Price | Closing price from NSE bhavcopy |
| Last Updated | Time when the automation last ran |
| Bhavcopy Date | NSE trading data date used |

If these values appear, the first-stage automation is working correctly.

---

## Current Project Workflow

The current workflow is:

```text
NSE Bhavcopy Data
        ↓
Python Script
        ↓
Filter Equity Stocks
        ↓
Remove ETFs, Bonds, Liquid Funds, Gold, Silver, etc.
        ↓
Sort Stocks by Volume
        ↓
Select Top 250 Stocks
        ↓
Update Google Sheet
```

---

## Current Project Status

The first stage of the project is complete.

The system currently works as an automated NSE volume-data updater.

It successfully updates the Google Sheet with:

- NSE Code
- Volume
- Close Price
- Last Updated Time
- Bhavcopy Date

---

## Why Top 250 Volume Stocks Are Selected

NSE has thousands of traded stocks and securities. Checking all of them manually is time-consuming and creates unnecessary noise.

The top 250 highest-volume stocks are selected because:

1. They are the most actively traded stocks of the day.
2. High volume shows strong market participation.
3. Volume is an important confirmation factor for breakout analysis.
4. This creates a smaller and cleaner dataset for further screening.

---

## Future Work

The current project is only the first stage. Further work will include:

1. Adding Current Market Price.
2. Adding 50 DMA.
3. Adding 100 DMA.
4. Adding 200 DMA.
5. Checking whether each stock is above 50 DMA.
6. Checking whether each stock is above 100 DMA.
7. Checking whether each stock is above 200 DMA.
8. Checking whether the stock is not more than 10% above 200 DMA.
9. Adding CAR confirmation.
10. Creating a final filtered breakout stock list in the **Final List** tab.

The future workflow will be:

```text
Top 250 Volume Stocks
        ↓
50 DMA / 100 DMA / 200 DMA Check
        ↓
Breakout Condition Check
        ↓
CAR Confirmation
        ↓
Final List
```

---

## Security Notes

Do not share or upload the following publicly:

- JSON key file
- GCP_CREDENTIALS secret
- Private key text
- GitHub secrets

The Google Sheet output can be shared safely with Viewer access.

The GitHub repository should remain private unless the sensitive keys and secrets are removed.

---

## Disclaimer

This project is made for educational, automation, and data-analysis purposes only.

It does not provide buy or sell recommendations. Stock market investment decisions should not be made only on the basis of this sheet. Proper research and advice from a registered financial advisor should be taken before making any investment decision.

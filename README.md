[![build](https://github.com/c1t0d0s0/phs/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/c1t0d0s0/phs/actions/workflows/pages/pages-build-deployment)
[![release](https://img.shields.io/github/v/release/c1t0d0s0/phs)](https://github.com/c1t0d0s0/phs/releases/latest)
[![license](https://img.shields.io/github/license/c1t0d0s0/phs)](LICENSE)

# Overview

This project fetches weather, AMeDAS, tide, announcements, and related data on a schedule and displays them on a signage-oriented web page. GitHub Actions is used to fetch and update data periodically and to generate JSON for the front end (`docs` directory).

## Features & Data Sources

The following data is fetched automatically by GitHub Actions (cron) and saved as JSON under `docs/`.

1. **Japan Meteorological Agency (JMA) Forecast Data** (`docs/130000.json`)
   * **Source:** JMA Forecast API (`https://www.jma.go.jp/bosai/forecast/data/forecast/130000.json`)
   * **Region:** Tokyo (130000)
   * **Update frequency:** Daily at 06:10 JST (21:10 UTC)
   * **Workflow:** `.github/workflows/daily-jma-fetch.yml`

2. **AMeDAS Data** (`docs/44132.json`)
   * **Source:** JMA AMeDAS latest data
   * **Station:** Station code 44132 (Tokyo)
   * **Update frequency:** Every hour at 5 minutes past (JST)
   * **Workflow:** `.github/workflows/hourly-amedas-fetch.yml`
   * **Script:** `scripts/amedas.py`

3. **Tide, Sunrise & Sunset Data** (`docs/tide.json`)
   * **Source:** [tide736.net API](https://tide736.net/) (tide), Python library `astral` (sunrise/sunset)
   * **Location:** Shibaura area (lat: 35.6586, lon: 139.7454)
   * **Update frequency:** Daily at 00:10 JST (15:10 UTC)
   * **Workflow:** `.github/workflows/daily-tide-fetch.yml`
   * **Script:** `scripts/tide.py`

4. **RSS Feed Data** (`docs/rss.json`)
   * **Source:** RSS feed configured via Google Apps Script
   * **RSS feed URL:** Set by `RSS_URL` in `scripts/rss.py`
   * **Update frequency:** Every hour at 22 minutes past (JST)
   * **Workflow:** `.github/workflows/hourly-rss-fetch.yml`
   * **Script:** `scripts/rss.py`
   * **Media & Video Support:** Supports video playback (`.mp4`, `.mov`, `.webm`, `.m4v`) in addition to images (`.jpg`, `.png`, etc.). Videos are played automatically with audio muted. When duration is unspecified, playback time automatically syncs to the video duration. Downloaded media files are cached locally and automatically cleaned up when removed from the RSS feed.

5. **Japanese Public Holiday Data** (`docs/date.json`)
   * **Source:** `https://holidays-jp.github.io/api/v1/date.json`

## Directory Structure

* `docs/`: Front-end resources (HTML, CSS, JS) and auto-fetched JSON. Serves as the document root for static hosting (e.g. GitHub Pages).
  * `index.html`: Main dashboard
  * `weather.html`: Weather forecast dashboard
  * `tide.html`: Tide information page
  * `*.json`: Fetched data files
* `scripts/`: Python scripts for data fetching
  * `amedas.py`: AMeDAS fetch and formatting
  * `tide.py`: Tide, sunrise/sunset, and moon phase calculation and formatting
  * `rss.py`: RSS feed fetch
  * `requirements-*.txt`: Python package lists per script
  * `signage.gs`: Google Apps Script for RSS feed generation (set the spreadsheet ID in `SpreadsheetApp.openById()`)

## Local Run & Development

To test the data-fetch scripts locally, run:

```bash
# AMeDAS fetch test
pip install -r scripts/requirements-amedas.txt
python scripts/amedas.py

# Tide fetch test
pip install -r scripts/requirements-tide.txt
python scripts/tide.py

# RSS feed fetch test
pip install -r scripts/requirements-rss.txt
python scripts/rss.py docs
```

To preview the front end, start a local server and open the `docs/` directory:

```bash
cd docs
python -m http.server 8000
# Open http://localhost:8000 in your browser
```

## Updating Google Apps Script (signage.gs)

To update the Google Apps Script (GAS) Web App with the latest `scripts/signage.gs` code without changing the existing Web App URL (configured as `RSS_URL` in `scripts/rss.py`), update the deployment via **"Manage deployments"**:

1. **Open the Apps Script Editor**:
   * Open your Google Spreadsheet, then select "Extensions" > "Apps Script".
2. **Update the Code**:
   * Replace the editor code with the content of `scripts/signage.gs`.
   * Keep your existing spreadsheet ID in `SpreadsheetApp.openById("...")`.
   * Save the project (`Ctrl+S` / `Cmd+S`).
3. **Update Deployment (Preserves Existing URL)**:
   * Click the **"Deploy"** button in the top right and select **"Manage deployments"**.
     > ⚠️ **Note:** Do NOT select "New deployment", as that will generate a new URL. Always choose **"Manage deployments"** to maintain the current URL.
   * Select the active **"Web app"** deployment from the left sidebar.
   * Click the **pencil icon (Edit)** in the top right.
   * Under **"Version"**, select **"New version"**.
   * Click the **"Deploy"** button at the bottom right.
4. **Done**:
   * The updated code will now be served at the existing Web App URL.


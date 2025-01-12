# Teams Scraper

## Overview
This repository is dedicated to scraping, processing, and analyzing data related to American football teams from various sources. The project includes modules for web scraping, data transformation, and visualization, with results being published to Google Sheets and other outputs for further analysis.

## Features

### 1. Web Scraping
The repository includes scrapers for multiple platforms, such as:
- **Barttorvik**  
  - `barttorvik_scrapper.py`
  - `barttorvik_prediction_scrapper.py`

- **KenPom**  
  - `kenpom_scrapper.py`
  - `kenpom_selinium_scrapper.py`

- **EvanMiya**  
  - `evanmiya_scrapper.py`
  - `evanmiya_prediction_scrapper.py`

- **Haslametrics**  
  - `haslametrics_scrapper.py`
  - `haslametrics_prediction_scrapper.py`

- **OddsShark**  
  - `oddsshark_prediction.py`

- **TeamRankings**  
  - `teamrankings_scrapper.py`

### 2. Data Transformation and Processing
The repository contains scripts for processing and combining raw data into actionable insights:
- `data_processing.py`: Cleans and integrates scraped data.
- `process_prediction_data.py`: Processes prediction data to generate refined results.
- `dataframtoMysql.py`: Stores processed data into SQL tables for further querying.

### 3. Result Visualization
- `display_prediction_results.py`: Visualizes and exports prediction results for analysis.

### 4. Google Sheets Integration
Processed data can be published directly to Google Sheets using API integrations.

### 5. Discord Notifications
Automated Discord notifications are included in several workflows for status updates and results.

## Contributing
Feel free to open an issue or submit a pull request for suggestions or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

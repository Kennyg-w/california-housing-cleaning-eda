# California Housing — Data Cleaning & Exploratory Analysis

A data-analytics project on the California housing dataset (20,640 districts).
It cleans the data, explores what drives house prices, and produces an Excel
workbook plus charts. An interactive Excel version (housing_project.xlsx) also exists.

## Key findings
- Median income is the dominant driver of house value (r ~ 0.69).
- Coastal districts average ~2x inland values (inland ~ $125k).
- Prices fall sharply north of 38 degrees latitude (far north ~ $84k vs ~ $220k south).

## Run it
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python3 housing_analysis.py housing.csv

Outputs: housing_project.xlsx and charts/*.png

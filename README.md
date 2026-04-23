# 📰 Intelligent News Assistant

An end-to-end modular pipeline for automatically collecting, filtering,
analyzing, and summarizing news from major Vietnamese RSS sources.

------------------------------------------------------------------------

## 📌 Overview

**Intelligent News Assistant** is a data pipeline system designed to
ingest news articles from multiple RSS feeds, process and analyze
content using NLP techniques, and generate structured weekly reports.

The project emphasizes: - Modularity - Scalability - Maintainability

------------------------------------------------------------------------

## ✨ Key Features

### 🔹 Multi-source Ingestion

-   VnExpress\
-   Thanh Niên\
-   Tuổi Trẻ

### 🔹 Dynamic Filtering

-   Topic-based filtering\
-   Time range filtering

### 🔹 NLP-based Content Analysis

-   Keyword extraction\
-   Text summarization

### 🔹 Automated Reporting

-   Markdown report generation

------------------------------------------------------------------------

## 🏗️ Project Structure

    ├── main.py
    ├── config/
    ├── src/
    ├── data/
    ├── reports/
    └── requirements.txt

------------------------------------------------------------------------

## ⚙️ Installation

``` bash
python -m venv venv
```

Activate: - Windows: `venv\Scripts\activate` - macOS/Linux:
`source venv/bin/activate`

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

## 🚀 Usage

``` bash
python main.py
```

Custom:

``` bash
python main.py --days 7 --topic technology
python main.py --from 2026-04-01 --to 2026-04-07
```

------------------------------------------------------------------------

## 📊 Output

    reports/weekly_report_<YYYY-MM-DD_HHMMSS>_UTC.md (new file each run)

------------------------------------------------------------------------

## 📝 Submission Note
This project is developed as a part of a technical assessment - AI Engineer. 

**Copyright © 2026 Giang Le Huynh** Licensed under the [MIT License](LICENSE).

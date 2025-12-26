# Moscow Industrial Enterprises Monitoring System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Dash](https://img.shields.io/badge/Dash-Plotly-green.svg)](https://dash.plotly.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey.svg)](https://www.sqlite.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-orange.svg)](https://pandas.pydata.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An interactive web dashboard built with **Plotly Dash** designed to support the Department of Investment and Industrial Policy of Moscow. The application provides comprehensive monitoring and visualization of key performance indicators for industrial enterprises in Moscow, including revenue, employment, exports, investments, and environmental metrics.

Data is presented through intuitive charts, tables, and interactive maps, with powerful filtering capabilities by industry, district, and time period. Users can compare enterprises, identify trends, and export reports for further analysis.

Developed as a team student project at UNECON in 2025.

## Video Demo

[![Full Project Overview]<img width="1443" height="864" alt="image" src="https://github.com/user-attachments/assets/02593295-402b-44c2-9c0c-5bbc0ea0da58" />
](https://youtu.be/28Pzg3bkgkc)

Click on the thumbnail to watch the full demo video (overview of all dashboards, filters, maps, and features).

## Technologies

- **Python 3.8+**
- **Dash** & **Plotly** — interactive web interface and visualizations
- **Pandas** — data processing and analysis
- **SQLite** — centralized data storage
- **Requests** — integration with open data APIs
- **Dash Bootstrap Components** — responsive and modern UI

## Project Structure
<img width="698" height="713" alt="image" src="https://github.com/user-attachments/assets/bebef316-3d33-4eeb-a013-86e3d59d7476" />

## Features

### Data Management
- Automated data collection via the Moscow Open Data Portal API
- Centralized storage in SQLite with upsert mechanism for data freshness
- Normalized schema supporting over 150 attributes per enterprise

### Analytics Modules
- **Production Analysis** — monitoring output volumes, sales efficiency, capacity utilization
- **Financial & Economic Analysis** — revenue/profit dynamics, industry rankings
- **Investment Monitoring** — tracking investments, sector activity, attractiveness ranking
- **Export & Foreign Trade** — export volumes, geographic diversification, interactive world map of trade partners
- **Employment Analysis** — workforce size, average salary trends, segmentation by industry and district
- **Environmental Monitoring** — emissions tracking, eco-equipment presence, adoption of green technologies

### Geospatial Analytics
- Interactive map of enterprise locations
- Territorial industrial potential visualization
- Spatial display of environmental indicators and risks

### User Interaction
- Advanced filters (industry, district, year, etc.)
- Comparative enterprise analysis
- Export of charts, tables, and reports

## Data Sources

- Primary: [List of enterprises with industrial complex status](https://data.mos.ru/opendata/7710071979-perechen-predpriyatiy-poluchivshih-status-promyshlennogo-kompleksa) (Moscow Open Data Portal)
- Supplementary: synthetically generated data for demonstration purposes

Future development may include integration with Rosstat, Federal Tax Service, GISIP, and regional environmental registries.

## Installation & Running

### Requirements
```bash
pip install dash plotly pandas requests dash-bootstrap-components openpyxl
```

### Existing Solutions Analysis
The project draws inspiration from commercial and public platforms such as:

- SPARK-Interfax
- Centre for Cities Data Tool
- AMPER

The developed solution focuses on seamless open data integration, user-friendly visualization, and rapid updates tailored to Moscow's industrial ecosystem.

### Future Development

- Integration with additional official data sources
- Predictive analytics using machine learning
- Mobile-responsive interface
- Real-time alert system for critical indicator changes
- Automated report generation module

### Team

- [Anastasia Ovchinnikova](https://github.com/btwnastya2)
- Daria Vazhova
- Alina Ershova
- Yana Reuchenko
- Sofya Shashina

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

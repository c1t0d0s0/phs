```mermaid
flowchart LR
  subgraph GitHub[**GitHub**]
    repository[(Repository)]
    actions_deploy[Pages Build and Deployment]
    actions_forecast[daily Forecast fetch<br>GitHub Actions]
    actions_amedas[hourly AMeDAS fetch<br>GitHub Actions]
    actions_rss[hourly RSS fetch<br>GitHub Actions]
    actions_tide[daily Tide fetch<br>GitHub Actions]
    pages(GitHub Pages)
  end

  subgraph Google[**Google**]
    drive[(Google Drive)]
    apps[RSS Feed Generator<br>Apps Script]
  end

  subgraph JMA[**JMA**]
    forecast_api[Forecast API]
    amedas_api[AMeDAS API]
  end
  style JMA fill:#333333, stroke-dasharray: 5 5

  subgraph Tide[**Tide**]
    tide_api[Tide API]
  end
  style Tide fill:#333333, stroke-dasharray: 5 5

  subgraph Client[**Client**]
    web_browser[Web Browser]
  end
  style Client fill:#331111, stroke-dasharray: 5 5

  subgraph Operator[**Operator**]
    web_browser2[Web Browser]
  end
  style Operator fill:#331111, stroke-dasharray: 5 5

  repository --> actions_deploy
  actions_deploy -->|Deploy| pages

  drive -->|Spread Sheet| apps
  drive -->|Image Files| actions_rss
  apps -->|RSS Feed| actions_rss
  actions_rss -->|Deploy| pages

  forecast_api -->|Weather Forecast| actions_forecast
  actions_forecast -->|130000.json| repository

  amedas_api -->|AMeDAS Info| actions_amedas
  actions_amedas -->|44132.json| repository

  tide_api -->|Tide Info| actions_tide
  actions_tide -->|tide.json| repository

  pages --> web_browser

  web_browser2 -->|Edit Spread Sheet<br>Upload Image Files| drive
```

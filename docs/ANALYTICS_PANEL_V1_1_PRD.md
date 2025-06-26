# PRD · Analytics Panel v1.1 (Topic & Time-Series)

Owner Analytics Agent × GUI Agent  | Status Draft

---

## 1 · Problem
MVP shows totals and model usage but lacks deeper insight (topics, trends) and export.

## 2 · Goals
| # | Goal | Metric | Acceptance |
|---|------|--------|------------|
| A1 | Topic cloud (top tags) | Cloud renders in panel | Unit test returns ≥10 tags |
| A2 | Time-series line chart | QtChart line shows msgs/day | Visual inspection & unit test |
| A3 | CSV/PDF export | File saved via Export Center API | Smoke test verifies file exists |

## 3 · Non-Goals
Sentiment analysis (future). 3-D charts.

## 4 · Success Metrics
* Render time < 300 ms.  
* Export completes < 2 s for 10 k rows.

## 5 · Solution Outline
1. **Topic extraction** – simple TF-IDF over `memory_content_processor` outputs.  
2. **Line chart** – QtCharts `QLineSeries` fed by daily counts query.  
3. **Export** – delegate to Export Center (WeasyPrint → PDF, pandas → CSV).

## 6 · Timeline (2 days)
| Day | Deliverable |
|-----|-------------|
| 0.5 | TF-IDF utility + tests |
| 0.5 | Time-series SQL + chart stub |
| 0.5 | GUI wiring |
| 0.5 | Export button + smoke tests |

---

*Dependencies:* Export Center v1 API must exist before A3 final test. 
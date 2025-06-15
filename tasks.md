# Development Tasks

This project aims to build a command line and web based tool to display
pharmaceutical related data. Core features identified from `rules.md` are
summarized below with the corresponding development tasks.

## Core Features
1. Load laboratory results, microbiology reports and medication
   information from either local JSON files or API calls.
2. Convert ROC date strings into Python `datetime` objects.
3. Present the data in tables and charts. Lab and microbiology results are
   rendered as grouped tables. Medication records are visualised with a
   Gantt chart.
4. Provide a CLI that accepts patient number and date range and outputs an
   HTML report. WebUI is planned later but shares the same processing
   logic.
5. Support filtering of default/supplementary/other laboratory items.
6. Offer an export function to generate a standalone HTML file that embeds
data for client‑side filtering.

## Task Breakdown

1. **Data Loading**
   - Read JSON files under `data/` for a given patient number.
   - Implement optional API fetch in the future.
   - Handle potential UTF‑8 BOM when opening files.

2. **Date Utilities**
   - Implement `convert_roc_date(date_str, fmt)` to convert ROC dates such as
     `1140605152343` or `114.06.08` to `datetime`.

3. **Laboratory Data Processing**
   - Group items by `code_desc` and by `testname`.
   - Collect results for each date column sorted by time.
   - Mark values outside `normal_range` for highlighting.
   - Provide filtering by item category (default/supplementary/other).

4. **Microbiology Data Processing**
   - Group records by `SpecName` then `DicName`.
   - Combine `OrganRptSub` entries by date/time.
   - Include antibiotic susceptibility (`RisRptSub`) as sub‑tables.

5. **Medication Data Processing**
   - Parse current doctor orders (`現狀藥囑.json`).
   - Parse nursing administration records (`護理給藥.json`).
   - Build a timeline of medication use with start and stop times.
   - Produce a Gantt chart using Matplotlib.

6. **HTML Report Generation**
   - Render tables for laboratory and microbiology data.
   - Embed the medication Gantt chart image.
   - Insert patient information and export date in the header.
   - Include client‑side JavaScript for filtering.

7. **Command Line Interface**
   - Provide options: patient number, start date, end date, output path,
     filtering presets.
   - Execute data loading, processing and HTML generation.

8. **Testing (future)**
   - Prepare unit tests for data conversion and processing functions using
     `pytest` once the modules are stable.


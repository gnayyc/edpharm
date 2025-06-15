# Data Definitions

The `data/` directory contains several JSON files used to emulate API
responses. Each patient has a set of files with the same structure. The
following sections document the fields observed in these files and how they
relate to the tables and charts described in `rules.md`.

## 1. Laboratory Results (`*_檢驗.json`)

An array of test records:

- `patnum` – patient number.
- `ordernum` – order identifier.
- `reqdatetime` – request time in ROC format `YYYMMDDHHMMSS`.
- `arrivaldatetime` – specimen arrival time, same format.
- `resdt` – result time, same format.
- `testname` – name of the laboratory test.
- `result` – numeric or textual result.
- `normal_range` – reference range text.
- `unit` – unit of measure.
- `testcode` – internal code.
- `comments` – optional comment field.
- `testorder` – order sequence number.
- `resflag` – abnormal flag ("H"/"L" etc.).
- `code_desc` – broader category of the test.

These records are displayed as a table grouped by `code_desc`. Each row is a
test name, and each column represents a date. Results are sorted by time
within the same date. Values outside the normal range are highlighted.

## 2. Microbiology Reports (`*_微生物報告.json`)

An array where each item contains:

- `RptDate` – report date in ROC format `YYY.MM.DD`.
- `RptTime` – report time `HH:MM:SS`.
- `ChartNo` – patient number.
- `OrganUnicode` – report identifier.
- `OrganCount` – count of organisms.
- `Status` – preliminary or final.
- `SpecName` – specimen type (e.g. Blood, Urine).
- `DicName` – examination name.
- `OrganRptSub` – list of organism findings with fields
  `OrganName`, `RptDate`, `RptTime`.
- `RisRptSub` – list of antibiotic susceptibility entries, usually with
  antibiotic, MIC and interpretation.

The table groups entries by `SpecName`. Each row shows `DicName` and culture
results by date, with susceptibility data presented in a nested table.

## 3. Viral Reports (`*_病毒類報告.json`)

Simple array with:

- `rpt_date` – ROC date string `YYY.MM.DD`.
- `rpt_time` – report time.
- `dic_name` – test name.
- `result` – textual result.
- `remark` – comments.

Displayed similarly to laboratory results but usually shorter.

## 4. Current Medication Orders (`*_現狀藥囑.json`)

Array fields:

- `alise_desc` – drug name.
- `unit_desc` – dose unit.
- `fee_unit_desc` – billing unit.
- `qty` – dose per administration.
- `cir_code` – frequency (e.g. BID, Q12H).
- `path_code` – route (PO, IV...).
- `start_date` / `start_time` – start of the order (ROC `YYYMMDD` + `HHMM`).
- `tqty` – total quantity per day.
- `days` – number of days prescribed.
- `dc_date` / `dc_time` – stop date/time.
- `ipd_seq` – hospitalisation sequence number.
- `order_date` – order date.

These dates define the medication bars on the Gantt chart.

## 5. Nursing Administration Records (`*_護理給藥.json`)

Array fields:

- `ConfOper` – nurse code.
- `ConfDate` / `ConfTime` – confirmation time (ROC `YYYMMDD` + `HHMM`).
- `Qty` – administered quantity.
- `UnitDesc` – unit text.
- `AliseDesc` – drug name.

These points are plotted on top of the medication bars to indicate actual
doses.

## 6. Other Files

`*_現狀醫囑.json`, `*_放射科報告內容.json`, `*_染色體報告.json`, and
`*_一周的檢查清單.json` contain various hospital data (orders, radiology
reports, chromosomal reports, and weekly examinations). They follow a similar
pattern of key/value pairs with ROC dates and are used for supplementary
pages in the exported report.


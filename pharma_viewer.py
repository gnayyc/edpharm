import argparse
import json
from datetime import datetime, date, time
from collections import defaultdict
from pathlib import Path
import re

try:
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover - optional dependency
    plt = None


ROC_OFFSET = 1911


def load_json(path):
    """Load JSON file and strip UTF-8 BOM if present."""
    data = Path(path).read_bytes()
    # Remove BOM if exists
    if data.startswith(b"\xef\xbb\xbf"):
        data = data[3:]
    return json.loads(data.decode('utf-8'))


def parse_roc_datetime(value: str) -> datetime:
    """Convert various ROC date formats to datetime."""
    value = value.strip()
    if not value:
        raise ValueError("empty date string")
    if '.' in value:
        # Format: YYY.MM.DD
        parts = value.split('.')
        if len(parts) >= 3:
            y, m, d = parts[:3]
            return datetime(int(y) + ROC_OFFSET, int(m), int(d))
    if len(value) == 13:
        y = int(value[0:3]) + ROC_OFFSET
        m = int(value[3:5])
        d = int(value[5:7])
        hh = int(value[7:9])
        mm = int(value[9:11])
        ss = int(value[11:13])
        return datetime(y, m, d, hh, mm, ss)
    if len(value) == 11:
        y = int(value[0:3]) + ROC_OFFSET
        m = int(value[3:5])
        d = int(value[5:7])
        hh = int(value[7:9])
        mm = int(value[9:11])
        return datetime(y, m, d, hh, mm)
    if len(value) == 7:
        y = int(value[0:3]) + ROC_OFFSET
        m = int(value[3:5])
        d = int(value[5:7])
        return datetime(y, m, d)
    raise ValueError(f"Unknown ROC date format: {value}")


def process_lab_data(records):
    """Group lab data for table generation."""
    grouped = defaultdict(lambda: defaultdict(list))
    dates = set()
    for rec in records:
        category = (rec.get('code_desc') or '').strip()
        test = (rec.get('testname') or '').strip()
        try:
            dt = parse_roc_datetime(rec['reqdatetime'])
        except Exception:
            continue
        dates.add(dt.date())
        grouped[category][test].append((dt, rec))
    # Sort entries
    for cat in grouped.values():
        for test in cat:
            cat[test].sort(key=lambda x: x[0])
    return sorted(dates), grouped


def process_microbio_data(records):
    grouped = defaultdict(lambda: defaultdict(list))
    dates = set()
    for rec in records:
        spec = rec.get('SpecName', '').strip()
        dic = rec.get('DicName', '').strip()
        try:
            dt = parse_roc_datetime(rec['RptDate'])
        except Exception:
            continue
        dates.add(dt.date())
        results = []
        for sub in rec.get('OrganRptSub', []):
            org = sub.get('OrganName', '').strip()
            if org:
                results.append(org)
        grouped[spec][dic].append((dt, results, rec.get('RisRptSub', [])))
    for spec in grouped.values():
        for dic in spec:
            spec[dic].sort(key=lambda x: x[0])
    return sorted(dates), grouped


def process_medication(orders, nursing):
    items = []
    for order in orders:
        start = parse_roc_datetime(order['start_date'] + order['start_time'])
        end = parse_roc_datetime(order['dc_date'] + order['dc_time'])
        label = order['alise_desc'].strip()
        freq = order.get('cir_code', '').strip()
        dose = order.get('qty')
        items.append({'label': label, 'start': start, 'end': end,
                      'freq': freq, 'dose': dose})
    items.sort(key=lambda x: (x['start'], x['label']))
    administrations = []
    for rec in nursing:
        dt = parse_roc_datetime(rec['ConfDate'] + rec['ConfTime'])
        administrations.append({'drug': rec['AliseDesc'].strip(), 'time': dt})
    return items, administrations


def plot_gantt(items, administrations, path):
    if not items or plt is None:
        return None
    fig, ax = plt.subplots(figsize=(8, 0.4 * len(items) + 1))
    ylabels = []
    for idx, item in enumerate(items):
        start = item['start']
        end = item['end']
        ax.barh(idx, (end - start).total_seconds() / 3600, left=start,
                 height=0.4, color='skyblue')
        ylabels.append(f"{item['label']} {item['dose']} {item['freq']}")
    ax.set_yticks(range(len(items)))
    ax.set_yticklabels(ylabels)
    ax.invert_yaxis()
    for adm in administrations:
        for idx, item in enumerate(items):
            if adm['drug'] == item['label']:
                ax.plot(adm['time'], idx, 'ro', markersize=3)
    fig.autofmt_xdate()
    plt.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    return path


def generate_html(patient, lab_dates, lab_data, micro_dates, micro_data, gantt_path, output):
    def fmt_date(d):
        return d.strftime('%Y-%m-%d')

    html = ["<html><head><meta charset='utf-8'><title>Pharma Data</title></head><body>"]
    html.append(f"<h1>Patient {patient}</h1>")
    if lab_data:
        html.append("<h2>Laboratory Data</h2>")
        html.append("<table border='1'>")
        header = "<tr><th>Category</th><th>Test</th>" + ''.join(f"<th>{fmt_date(d)}</th>" for d in lab_dates) + "</tr>"
        html.append(header)
        for cat, tests in lab_data.items():
            for test, entries in tests.items():
                row = f"<tr><td>{cat}</td><td>{test}</td>"
                results_by_date = {dt.date(): rec.get('result') for dt, rec in entries}
                for d in lab_dates:
                    val = results_by_date.get(d, '')
                    row += f"<td>{val}</td>"
                row += "</tr>"
                html.append(row)
        html.append("</table>")
    if micro_data:
        html.append("<h2>Microbiology</h2>")
        html.append("<table border='1'>")
        header = "<tr><th>Specimen</th><th>Test</th>" + ''.join(f"<th>{fmt_date(d)}</th>" for d in micro_dates) + "</tr>"
        html.append(header)
        for spec, tests in micro_data.items():
            for dic, entries in tests.items():
                row = f"<tr><td>{spec}</td><td>{dic}</td>"
                by_date = defaultdict(list)
                for dt, results, _ in entries:
                    by_date[dt.date()].extend(results)
                for d in micro_dates:
                    val = '; '.join(by_date.get(d, []))
                    row += f"<td>{val}</td>"
                row += "</tr>"
                html.append(row)
        html.append("</table>")
    if gantt_path:
        html.append("<h2>Medication Timeline</h2>")
        html.append(f"<img src='{Path(gantt_path).name}' alt='gantt'>")
    html.append("</body></html>")
    Path(output).write_text('\n'.join(html), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description="Generate pharma HTML report")
    parser.add_argument('patient')
    parser.add_argument('--output', default='report.html')
    args = parser.parse_args()

    pid = args.patient
    base = Path('data')
    lab_file = base / f"{pid}_檢驗.json"
    micro_file = base / f"{pid}_微生物報告.json"
    order_file = base / f"{pid}_現狀藥囑.json"
    nurse_file = base / f"{pid}_護理給藥.json"

    lab_data = load_json(lab_file) if lab_file.exists() else []
    micro_data = load_json(micro_file) if micro_file.exists() else []
    orders = load_json(order_file) if order_file.exists() else []
    nursing = load_json(nurse_file) if nurse_file.exists() else []

    lab_dates, lab_grouped = process_lab_data(lab_data)
    micro_dates, micro_grouped = process_microbio_data(micro_data)
    meds, admin = process_medication(orders, nursing)

    gantt_path = None
    if meds and plt is not None:
        gantt_path = Path(args.output).with_suffix('.png')
        plot_gantt(meds, admin, gantt_path)

    generate_html(pid, lab_dates, lab_grouped, micro_dates, micro_grouped,
                  gantt_path, args.output)
    if gantt_path and Path(gantt_path).exists():
        print(f"Gantt chart saved to {gantt_path}")
    print(f"HTML report saved to {args.output}")


if __name__ == '__main__':
    main()

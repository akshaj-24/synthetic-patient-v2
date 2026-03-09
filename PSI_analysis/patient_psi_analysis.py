import json
from collections import Counter
import plotly.graph_objects as go
import json as _json

with open("PSI_CM_data.json", "r") as f:
    patients = json.load(f)

n_patients = len(patients)

def flatten(patients, field, split_commas=False):
    items = []
    for p in patients:
        for v in p.get(field, []):
            if split_commas:
                items += [e.strip() for e in v.split(",")]
            else:
                items.append(v.strip())
    return items

def per_patient_counts(patients, field, split_commas=False):
    value_patient_sets = {}
    for p in patients:
        seen = set()
        for v in p.get(field, []):
            vals = [e.strip() for e in v.split(",")] if split_commas else [v.strip()]
            seen.update(vals)
        for val in seen:
            value_patient_sets.setdefault(val, set()).add(p["id"])
    return {val: len(ids) for val, ids in value_patient_sets.items()}

def build_distribution(patients, field, split_commas=False, label=""):
    raw_counts = Counter(flatten(patients, field, split_commas))
    patient_counts = per_patient_counts(patients, field, split_commas)
    rows = sorted(raw_counts.items(), key=lambda x: -x[1])
    return {
        "label": label,
        "values": [r[0] for r in rows],
        "n_patients": [patient_counts.get(r[0], 0) for r in rows],
        "prob": [round(patient_counts.get(r[0], 0) / n_patients, 3) for r in rows],
    }

# ── All 5 fields ─────────────────────────────────────────────────
fields = [
    ("type",                     False, "Comm. Type",      "comm_type.png"),
    ("emotion",                  True,  "Emotion",         "emotion.png"),
]

for field, split, label, fname in fields:
    d = build_distribution(patients, field, split, label)

    if not d["values"]:
        print(f"Skipped {label} — no data")
        continue

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=d["prob"],
        y=d["values"],
        orientation="h",
        text=[f"p={p}  (n={n})" for p, n in zip(d["prob"], d["n_patients"])],
        textposition="outside",
        showlegend=False,
        cliponaxis=False,
    ))
    fig.update_xaxes(title_text="P(patient)", range=[0, 1.3])
    fig.update_yaxes(automargin=True)
    fig.update_layout(
        title={"text": f"{label} Distribution (n={n_patients})"},
        height=max(800, 70 * len(d["values"])),
    )
    fig.write_image(fname)
    with open(f"{fname}.meta.json", "w") as mf:
        _json.dump({"caption": f"{label} distribution across {n_patients} patients"}, mf)
    print(f"Saved → {fname}")

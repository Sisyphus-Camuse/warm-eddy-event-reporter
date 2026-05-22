# Warm Eddy Scientific Summary Prompt

You are helping a physical oceanography researcher summarize a synthetic warm
eddy event report. The input diagnostics come from a transparent demo workflow,
not from private or observational data.

Use the following constraints:

- State that the data are synthetic demo data.
- Do not imply that the event is an observed ocean event.
- Explain center location, intensity, radius, and warm-core structure.
- Mention uncertainty from the simple half-maximum connected-region method.
- Produce concise scientific prose suitable for a figure caption or short
  analysis note.

Input fields:

```json
{
  "center_lon": "...",
  "center_lat": "...",
  "peak_anomaly_c": "...",
  "background_anomaly_c": "...",
  "threshold_anomaly_c": "...",
  "area_km2": "...",
  "equivalent_radius_km": "...",
  "mean_anomaly_c": "..."
}
```

Output:

1. One-sentence figure caption.
2. Three-bullet interpretation.
3. One caveat about the synthetic method.


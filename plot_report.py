"""Create a PNG heatmap and Markdown report for the synthetic warm eddy event."""

from __future__ import annotations

import argparse
import csv
import json
import math
import struct
import zlib
from pathlib import Path


DEFAULT_DATA = Path("data/synthetic_warm_eddy_sst_anomaly.csv")
DEFAULT_DETECTION = Path("outputs/synthetic_warm_eddy_detection.json")
DEFAULT_OUTPUT_DIR = Path("outputs")
PNG_NAME = "synthetic_warm_eddy_map.png"
REPORT_NAME = "synthetic_warm_eddy_report.md"


def read_matrix_csv(path: Path) -> tuple[list[float], list[float], list[list[float]]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        rows = list(reader)

    lons = [float(value) for value in rows[0][1:]]
    lats: list[float] = []
    values: list[list[float]] = []
    for row in rows[1:]:
        lats.append(float(row[0]))
        values.append([float(value) for value in row[1:]])
    return lons, lats, values


def interpolate_color(left: tuple[int, int, int], right: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(round(left[index] + (right[index] - left[index]) * t) for index in range(3))


def anomaly_color(value: float, lower: float, upper: float) -> tuple[int, int, int]:
    if upper <= lower:
        return (240, 240, 240)
    t = max(0.0, min(1.0, (value - lower) / (upper - lower)))

    blue = (45, 86, 158)
    white = (246, 247, 241)
    orange = (215, 117, 54)
    red = (154, 35, 42)

    if t < 0.5:
        return interpolate_color(blue, white, t / 0.5)
    if t < 0.82:
        return interpolate_color(white, orange, (t - 0.5) / 0.32)
    return interpolate_color(orange, red, (t - 0.82) / 0.18)


def png_chunk(kind: bytes, data: bytes) -> bytes:
    checksum = zlib.crc32(kind + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", checksum)


def write_png_rgb(path: Path, pixels: list[list[tuple[int, int, int]]]) -> None:
    height = len(pixels)
    width = len(pixels[0])
    raw_rows = []
    for row in pixels:
        raw_rows.append(b"\x00" + b"".join(bytes(rgb) for rgb in row))
    raw = b"".join(raw_rows)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += png_chunk(b"IHDR", ihdr)
    png += png_chunk(b"IDAT", zlib.compress(raw, level=9))
    png += png_chunk(b"IEND", b"")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)


def closest_index(values: list[float], target: float) -> int:
    return min(range(len(values)), key=lambda index: abs(values[index] - target))


def render_heatmap(
    lons: list[float],
    lats: list[float],
    values: list[list[float]],
    detection: dict[str, object],
    scale: int,
) -> list[list[tuple[int, int, int]]]:
    flat = [value for row in values for value in row]
    lower = min(flat)
    upper = max(flat)
    center_i = closest_index(lats, float(detection["center_lat"]))
    center_j = closest_index(lons, float(detection["center_lon"]))

    pixels: list[list[tuple[int, int, int]]] = []
    for i, row in enumerate(values):
        expanded_rows = [[] for _ in range(scale)]
        for j, value in enumerate(row):
            color = anomaly_color(value, lower, upper)
            for local_i in range(scale):
                for local_j in range(scale):
                    is_center = abs(i - center_i) <= 1 and j == center_j or abs(j - center_j) <= 1 and i == center_i
                    if is_center and (local_i in (0, scale - 1) or local_j in (0, scale - 1)):
                        expanded_rows[local_i].append((20, 20, 20))
                    else:
                        expanded_rows[local_i].append(color)
        pixels.extend(expanded_rows)

    return pixels


def write_report(path: Path, png_name: str, detection: dict[str, object]) -> None:
    report = f"""# Synthetic Warm Eddy Event Report

This report was generated from synthetic demo data. It does not contain private
research data, observational products, thesis material, or local machine paths.

![Synthetic warm eddy map]({png_name})

## Detection Summary

| Metric | Value |
| --- | ---: |
| Center longitude | {detection["center_lon"]} degE |
| Center latitude | {detection["center_lat"]} degN |
| Peak SST anomaly | {detection["peak_anomaly_c"]} degC |
| Background anomaly | {detection["background_anomaly_c"]} degC |
| Half-maximum threshold | {detection["threshold_anomaly_c"]} degC |
| Connected warm cells | {detection["region_cell_count"]} |
| Approximate area | {detection["area_km2"]} km2 |
| Equivalent radius | {detection["equivalent_radius_km"]} km |
| Mean anomaly in region | {detection["mean_anomaly_c"]} degC |

## Method

The detector uses a transparent baseline method: it finds the warmest grid
point, estimates the background from border cells, and extracts the connected
region above the half-maximum anomaly threshold around the peak.

## AI Copilot Extension

The prompt in `prompts/summary_prompt.md` can be used by a future AI-assisted
workflow to turn these diagnostics into a short scientific interpretation,
figure caption, or multi-date evolution summary. This demo does not call an API.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a PNG figure and Markdown report.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--detection", type=Path, default=DEFAULT_DETECTION)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--scale", type=int, default=5)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.scale < 1:
        raise SystemExit("--scale must be at least 1")

    lons, lats, values = read_matrix_csv(args.data)
    detection = json.loads(args.detection.read_text(encoding="utf-8"))

    png_path = args.output_dir / PNG_NAME
    report_path = args.output_dir / REPORT_NAME
    pixels = render_heatmap(lons, lats, values, detection, args.scale)
    write_png_rgb(png_path, pixels)
    write_report(report_path, PNG_NAME, detection)

    print(f"Wrote PNG figure: {png_path}")
    print(f"Wrote Markdown report: {report_path}")


if __name__ == "__main__":
    main()


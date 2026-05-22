"""Detect a synthetic warm eddy from a CSV sea-surface temperature anomaly field."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import deque
from pathlib import Path


DEFAULT_INPUT = Path("data/synthetic_warm_eddy_sst_anomaly.csv")
DEFAULT_OUTPUT = Path("outputs/synthetic_warm_eddy_detection.json")
KM_PER_DEGREE_LAT = 111.32


def read_matrix_csv(path: Path) -> tuple[list[float], list[float], list[list[float]]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        rows = list(reader)

    if len(rows) < 2 or len(rows[0]) < 2:
        raise ValueError(f"{path} does not look like a matrix CSV")

    lons = [float(value) for value in rows[0][1:]]
    lats: list[float] = []
    values: list[list[float]] = []
    for row in rows[1:]:
        lats.append(float(row[0]))
        values.append([float(value) for value in row[1:]])

    return lons, lats, values


def border_mean(values: list[list[float]]) -> float:
    top = values[0]
    bottom = values[-1]
    sides = [row[0] for row in values[1:-1]] + [row[-1] for row in values[1:-1]]
    border_values = top + bottom + sides
    return sum(border_values) / len(border_values)


def find_peak(values: list[list[float]]) -> tuple[int, int, float]:
    peak_i = 0
    peak_j = 0
    peak_value = values[0][0]
    for i, row in enumerate(values):
        for j, value in enumerate(row):
            if value > peak_value:
                peak_i = i
                peak_j = j
                peak_value = value
    return peak_i, peak_j, peak_value


def connected_region(values: list[list[float]], start: tuple[int, int], threshold: float) -> set[tuple[int, int]]:
    height = len(values)
    width = len(values[0])
    queue: deque[tuple[int, int]] = deque([start])
    seen = {start}
    region: set[tuple[int, int]] = set()

    while queue:
        i, j = queue.popleft()
        if values[i][j] < threshold:
            continue
        region.add((i, j))

        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                if di == 0 and dj == 0:
                    continue
                ni = i + di
                nj = j + dj
                if 0 <= ni < height and 0 <= nj < width and (ni, nj) not in seen:
                    seen.add((ni, nj))
                    queue.append((ni, nj))

    return region


def estimate_geometry(
    lons: list[float],
    lats: list[float],
    values: list[list[float]],
    region: set[tuple[int, int]],
) -> dict[str, float]:
    if not region:
        return {"area_km2": 0.0, "equivalent_radius_km": 0.0, "mean_anomaly_c": 0.0}

    dlon = abs(lons[1] - lons[0]) if len(lons) > 1 else 0.0
    dlat = abs(lats[1] - lats[0]) if len(lats) > 1 else 0.0
    mean_lat = sum(lats[i] for i, _ in region) / len(region)
    cell_width_km = KM_PER_DEGREE_LAT * math.cos(math.radians(mean_lat)) * dlon
    cell_height_km = KM_PER_DEGREE_LAT * dlat
    cell_area_km2 = abs(cell_width_km * cell_height_km)
    area_km2 = len(region) * cell_area_km2
    equivalent_radius_km = math.sqrt(area_km2 / math.pi)
    mean_anomaly_c = sum(values[i][j] for i, j in region) / len(region)

    return {
        "area_km2": round(area_km2, 2),
        "equivalent_radius_km": round(equivalent_radius_km, 2),
        "mean_anomaly_c": round(mean_anomaly_c, 4),
    }


def detect(lons: list[float], lats: list[float], values: list[list[float]]) -> dict[str, object]:
    peak_i, peak_j, peak_value = find_peak(values)
    background_c = border_mean(values)
    threshold_c = background_c + 0.5 * (peak_value - background_c)
    region = connected_region(values, (peak_i, peak_j), threshold_c)
    geometry = estimate_geometry(lons, lats, values, region)

    return {
        "dataset": "synthetic demo data",
        "method": "peak plus connected half-maximum warm region",
        "center_lon": round(lons[peak_j], 4),
        "center_lat": round(lats[peak_i], 4),
        "peak_anomaly_c": round(peak_value, 4),
        "background_anomaly_c": round(background_c, 4),
        "threshold_anomaly_c": round(threshold_c, 4),
        "region_cell_count": len(region),
        **geometry,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detect a warm eddy in synthetic demo data.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    lons, lats, values = read_matrix_csv(args.input)
    result = detect(lons, lats, values)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    print(f"Wrote detection result: {args.output}")


if __name__ == "__main__":
    main()


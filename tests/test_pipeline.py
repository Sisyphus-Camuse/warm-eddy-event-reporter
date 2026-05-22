from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_script(script: str, *args: str) -> None:
    command = [sys.executable, str(ROOT / script), *args]
    subprocess.run(command, cwd=ROOT, check=True)


class SyntheticPipelineTest(unittest.TestCase):
    def test_synthetic_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data_dir = root / "data"
            output_dir = root / "outputs"
            csv_path = data_dir / "synthetic_warm_eddy_sst_anomaly.csv"
            detection_path = output_dir / "synthetic_warm_eddy_detection.json"

            run_script("generate_sample.py", "--output-dir", str(data_dir), "--grid-size", "32")
            run_script("detect_eddy.py", "--input", str(csv_path), "--output", str(detection_path))
            run_script(
                "plot_report.py",
                "--data",
                str(csv_path),
                "--detection",
                str(detection_path),
                "--output-dir",
                str(output_dir),
            )

            detection = json.loads(detection_path.read_text(encoding="utf-8"))
            self.assertEqual(detection["dataset"], "synthetic demo data")
            self.assertGreater(detection["peak_anomaly_c"], 1.5)
            self.assertGreater(detection["equivalent_radius_km"], 20)
            self.assertTrue((output_dir / "synthetic_warm_eddy_map.png").exists())
            self.assertTrue((output_dir / "synthetic_warm_eddy_report.md").exists())


if __name__ == "__main__":
    unittest.main()

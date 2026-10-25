"""합성 기준점으로 유사변환의 수학적 성질과 CLI 실패를 검증한다."""

import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "roblox-real-world" / "scripts" / "fit_local_frame.py"
SPEC = importlib.util.spec_from_file_location("fit_local_frame", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def fixture(scale=3.5, angle=27, source_offset=(500000, 4200000), target_offset=(120, -80)):
    """실제 장소 자료를 포함하지 않는 임의의 미터 기준점이다."""
    a, b = scale * math.cos(math.radians(angle)), scale * math.sin(math.radians(angle))
    points = []
    for index, (e, n) in enumerate(((0, 0), (30, 0), (0, 20), (35, 15))):
        points.append({
            "id": str(index), "easting": source_offset[0] + e, "northing": source_offset[1] + n,
            "x": target_offset[0] + a * e - b * n,
            "z": target_offset[1] - b * e - a * n,
        })
    return {"crs": "LOCAL:TEST-METRES", "coordinate_type": "projected", "units": "m", "control_points": points}


class AlignmentTests(unittest.TestCase):
    def test_recovers_rotation_scale_and_each_control(self):
        data = fixture()
        result = MODULE.fit_local_frame(data, 1e-8)
        self.assertAlmostEqual(result["studs_per_meter"], 3.5, places=12)
        self.assertAlmostEqual(result["rotation_degrees"], 27, places=12)
        self.assertLess(result["max_error_studs"], 1e-10)
        origin, target, transform = result["source_origin"], result["roblox_origin"], result["transform"]
        for point in data["control_points"]:
            e, n = point["easting"] - origin["easting"], point["northing"] - origin["northing"]
            self.assertAlmostEqual(target["x"] + transform["a"] * e - transform["b"] * n, point["x"], places=8)
            self.assertAlmostEqual(target["z"] - transform["b"] * e - transform["a"] * n, point["z"], places=8)

    def test_large_absolute_coordinates_keep_local_fit(self):
        result = MODULE.fit_local_frame(fixture(source_offset=(1e12, -1e12)), 1e-6)
        self.assertAlmostEqual(result["studs_per_meter"], 3.5, places=10)
        self.assertLess(result["max_error_studs"], 1e-8)

    def test_exported_origin_avoids_rounded_centroid_at_large_coordinates(self):
        data = fixture(scale=2, angle=0, source_offset=(1e12, -1e12))
        data["control_points"] = [
            {"id": "A", "easting": 1e12, "northing": -1e12, "x": 10, "z": 20},
            {"id": "B", "easting": 1e12 + 1, "northing": -1e12, "x": 12, "z": 20},
            {"id": "C", "easting": 1e12, "northing": -1e12 + 1, "x": 10, "z": 18},
        ]
        result = MODULE.fit_local_frame(data, 1e-8)
        self.assertEqual(result["source_origin"], {"easting": 1e12, "northing": -1e12})
        self.assertLess(result["max_error_studs"], 1e-8)
        self.assertEqual(result["checks"]["threshold_status"], "passed")

    def test_north_is_negative_z_without_rotation(self):
        result = MODULE.fit_local_frame(fixture(scale=2, angle=0))
        self.assertAlmostEqual(result["transform"]["a"], 2)
        self.assertAlmostEqual(result["transform"]["b"], 0)

    def test_rejects_mirrored_targets(self):
        data = fixture()
        for point in data["control_points"]:
            point["z"] *= -1
        with self.assertRaisesRegex(MODULE.AlignmentError, "반전"):
            MODULE.fit_local_frame(data)

    def test_noise_is_visible_and_threshold_fails(self):
        data = fixture()
        data["control_points"][-1]["x"] += 4
        result = MODULE.fit_local_frame(data, 0.1)
        self.assertGreater(result["max_error_studs"], 0.1)
        self.assertEqual(result["checks"]["threshold_status"], "failed")

    def test_rejects_collinear_source_or_destination(self):
        for field in ("northing", "z"):
            data = fixture()
            for point in data["control_points"]:
                point[field] = 0
            with self.subTest(field=field), self.assertRaises(MODULE.AlignmentError):
                MODULE.fit_local_frame(data)

    def test_rejects_duplicate_points_and_identifiers(self):
        for fields in (("easting", "northing"), ("x", "z"), ("id",)):
            data = fixture()
            for field in fields:
                data["control_points"][1][field] = data["control_points"][0][field]
            with self.subTest(fields=fields), self.assertRaises(MODULE.AlignmentError):
                MODULE.fit_local_frame(data)

    def test_rejects_nonfinite_boolean_and_missing_values(self):
        for value in (math.nan, math.inf, -math.inf, True, "2", None, 10**1000):
            data = fixture()
            data["control_points"][0]["x"] = value
            with self.subTest(value=type(value).__name__), self.assertRaises(MODULE.AlignmentError):
                MODULE.fit_local_frame(data)

    def test_requires_declared_projected_metre_coordinates(self):
        for field, value in (("crs", "EPSG:4326"), ("crs", ""), ("units", "degree"), ("coordinate_type", "geographic")):
            data = fixture()
            data[field] = value
            with self.subTest(field=field), self.assertRaises(MODULE.AlignmentError):
                MODULE.fit_local_frame(data)
        data = fixture()
        data["control_points"][0]["latitude"] = 35
        with self.assertRaises(MODULE.AlignmentError):
            MODULE.fit_local_frame(data)

    def test_cli_json_and_threshold_exit_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "points.json"
            source.write_text(json.dumps(fixture()), encoding="utf-8")
            passed = subprocess.run([sys.executable, "-X", "utf8", str(SCRIPT), str(source), "--max-error-studs", "0.01"], capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(passed.returncode, 0, passed.stderr)
            self.assertEqual(json.loads(passed.stdout)["checks"]["threshold_status"], "passed")
            data = fixture()
            data["control_points"][-1]["x"] += 4
            source.write_text(json.dumps(data), encoding="utf-8")
            failed = subprocess.run([sys.executable, "-X", "utf8", str(SCRIPT), str(source), "--max-error-studs", "0.01"], capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(failed.returncode, 2)
            self.assertEqual(json.loads(failed.stdout)["checks"]["threshold_status"], "failed")

    def test_cli_rejects_nonstandard_json_and_nan_threshold(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "points.json"
            for content, args in (
                ("{\"x\": NaN}", []),
                ('{"x": ' + "9" * 5000 + "}", []),
                (json.dumps(fixture()), ["--max-error-studs", "nan"]),
            ):
                source.write_text(content, encoding="utf-8")
                result = subprocess.run([sys.executable, "-X", "utf8", str(SCRIPT), str(source), *args], capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, "")
                self.assertIn("정합 오류", result.stderr)


if __name__ == "__main__":
    unittest.main()

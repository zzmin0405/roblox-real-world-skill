#!/usr/bin/env python3
"""미터 투영좌표와 Roblox 기준점에서 평면 유사변환을 추정한다.

북쪽은 회전 0도에서 -Z이며, 높이와 좌표계 변환은 계산하지 않는다.
입력 JSON만 읽고 결과 JSON을 표준 출력으로 내보낸다.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


class AlignmentError(ValueError):
    """입력 또는 기준점 정합이 유효하지 않다."""


def finite_number(value: object, field: str) -> float:
    """불리언과 무한대가 아닌 유한한 숫자를 반환한다."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise AlignmentError(f"{field}: 유한한 숫자가 필요합니다.")
    try:
        number = float(value)
    except (OverflowError, ValueError) as exc:
        raise AlignmentError(f"{field}: 표현 가능한 유한한 숫자가 필요합니다.") from exc
    if not math.isfinite(number):
        raise AlignmentError(f"{field}: NaN 또는 Infinity를 사용할 수 없습니다.")
    return number


def centered(points: list[tuple[float, float]], label: str):
    """큰 절대좌표를 먼저 평행이동하고 기준점의 퇴화를 검사한다."""
    if len(set(points)) != len(points):
        raise AlignmentError(f"{label}: 서로 다른 기준점에 중복 좌표가 있습니다.")
    # 전체 좌표 합보다 첫 점과의 작은 차이를 합산해 큰 투영좌표에 대응한다.
    base_x, base_y = points[0]
    differences = [(x - base_x, y - base_y) for x, y in points]
    if not all(math.isfinite(value) for point in differences for value in point):
        raise AlignmentError(f"{label}: 좌표 범위가 너무 큽니다.")
    mean_x = math.fsum(x for x, _ in differences) / len(points)
    mean_y = math.fsum(y for _, y in differences) / len(points)
    local = [(x - mean_x, y - mean_y) for x, y in differences]
    extent = max(max(abs(x), abs(y)) for x, y in local)
    if extent == 0:
        raise AlignmentError(f"{label}: 기준점이 한 점으로 겹칩니다.")
    normalized = [(x / extent, y / extent) for x, y in local]
    xx = math.fsum(x * x for x, _ in normalized)
    yy = math.fsum(y * y for _, y in normalized)
    xy = math.fsum(x * y for x, y in normalized)
    if xx * yy - xy * xy <= 1e-12 * (xx + yy) ** 2:
        raise AlignmentError(f"{label}: 기준점이 한 직선에 있거나 거의 공선입니다.")
    return (base_x, base_y), local, normalized, extent, (mean_x, mean_y)


def fit_local_frame(data: object, max_error_studs: float | None = None) -> dict:
    """최소제곱 평면 유사변환과 각 기준점의 실제 잔차를 계산한다."""
    if not isinstance(data, dict):
        raise AlignmentError("입력 최상위는 JSON 객체여야 합니다.")
    crs = data.get("crs")
    if not isinstance(crs, str) or not crs.strip():
        raise AlignmentError("crs에 원본의 투영좌표계 식별자를 적어야 합니다.")
    if data.get("coordinate_type") != "projected" or data.get("units") != "m":
        raise AlignmentError("coordinate_type=projected, units=m인 투영좌표만 받습니다.")
    normalized_crs = crs.strip().upper().replace(" ", "")
    if normalized_crs in {"EPSG:4326", "EPSG:4979", "OGC:CRS84", "CRS84"}:
        raise AlignmentError("위경도 좌표계는 직접 정합할 수 없습니다. 먼저 미터 투영좌표로 변환하세요.")
    points = data.get("control_points")
    if not isinstance(points, list) or len(points) < 3:
        raise AlignmentError("control_points에 비공선 기준점 3개 이상이 필요합니다.")
    if max_error_studs is not None:
        max_error_studs = finite_number(max_error_studs, "max_error_studs")
        if max_error_studs < 0:
            raise AlignmentError("max_error_studs는 0 이상이어야 합니다.")

    ids: list[str] = []
    source: list[tuple[float, float]] = []
    target: list[tuple[float, float]] = []
    for index, point in enumerate(points):
        label = f"control_points[{index}]"
        if not isinstance(point, dict):
            raise AlignmentError(f"{label}: JSON 객체가 필요합니다.")
        if any(key in point for key in ("lat", "lon", "lng", "latitude", "longitude")):
            raise AlignmentError(f"{label}: 위경도 대신 미터 단위 easting/northing을 사용하세요.")
        point_id = point.get("id")
        if not isinstance(point_id, str) or not point_id.strip() or point_id in ids:
            raise AlignmentError(f"{label}.id: 비어 있지 않은 고유 문자열이 필요합니다.")
        ids.append(point_id)
        source.append(tuple(finite_number(point.get(key), f"{label}.{key}") for key in ("easting", "northing")))
        # -Z를 평면의 양의 북쪽 축으로 변환해 회전+양의 축척만 적합한다.
        x = finite_number(point.get("x"), f"{label}.x")
        z = finite_number(point.get("z"), f"{label}.z")
        target.append((x, -z))

    source_origin, source_local, source_norm, source_extent, source_mean = centered(source, "원본 좌표")
    target_base, target_local, target_norm, target_extent, target_mean = centered(target, "Roblox 좌표")
    cxx = math.fsum(e * x for (e, _), (x, _) in zip(source_norm, target_norm))
    cxy = math.fsum(e * q for (e, _), (_, q) in zip(source_norm, target_norm))
    cyx = math.fsum(n * x for (_, n), (x, _) in zip(source_norm, target_norm))
    cyy = math.fsum(n * q for (_, n), (_, q) in zip(source_norm, target_norm))
    determinant = cxx * cyy - cxy * cyx
    covariance_size = max(abs(cxx), abs(cxy), abs(cyx), abs(cyy))
    if determinant < -1e-12 * covariance_size**2:
        raise AlignmentError("기준점 대응이 좌우 반전되어 있습니다. X/Z 축과 기준점 대응을 확인하세요.")

    denominator = math.fsum(e * e + n * n for e, n in source_norm)
    ratio = target_extent / source_extent
    a = (cxx + cyy) / denominator * ratio
    b = (cxy - cyx) / denominator * ratio
    scale = math.hypot(a, b)
    if not all(math.isfinite(value) for value in (a, b, scale)) or scale <= 0:
        raise AlignmentError("양의 유한한 축척을 추정할 수 없습니다. 기준점 대응을 확인하세요.")

    # 공개 원점은 정확히 입력된 첫 점을 사용한다. 큰 좌표에 소수 평균을 더해
    # 반올림된 중심점을 내보내면 출력 변환의 잔차가 내부 잔차와 달라질 수 있다.
    target_origin = (
        target_base[0] + math.fsum((target_mean[0], -a * source_mean[0], b * source_mean[1])),
        target_base[1] + math.fsum((target_mean[1], -b * source_mean[0], -a * source_mean[1])),
    )
    residuals = []
    for point_id, (easting, northing), (x, q) in zip(ids, source, target):
        e, n = easting - source_origin[0], northing - source_origin[1]
        dx = target_origin[0] + a * e - b * n - x
        dz = -target_origin[1] - b * e - a * n + q
        error = math.hypot(dx, dz)
        if not all(math.isfinite(value) for value in (dx, dz, error)):
            raise AlignmentError("잔차 계산 범위가 너무 큽니다.")
        residuals.append({"id": point_id, "dx_studs": dx, "dz_studs": dz, "error_studs": error})
    errors = [item["error_studs"] for item in residuals]
    maximum = max(errors)
    # 큰 오차의 제곱 오버플로를 피한다.
    rmse = maximum * math.sqrt(math.fsum((error / maximum) ** 2 for error in errors) / len(errors)) if maximum else 0.0
    threshold_status = "not_requested" if max_error_studs is None else ("passed" if maximum <= max_error_studs else "failed")
    return {
        "crs": crs.strip(),
        "units": "m",
        "axis_convention": "회전 0도에서 동쪽=+X, 북쪽=-Z. +Y 높이는 정합하지 않음.",
        "source_origin": {"easting": source_origin[0], "northing": source_origin[1]},
        "roblox_origin": {"x": target_origin[0], "z": -target_origin[1]},
        "studs_per_meter": scale,
        "rotation_degrees": math.degrees(math.atan2(b, a)),
        "rotation_convention": "X/-Z 평면에서 +X를 -Z 쪽으로 돌리는 방향이 양의 각도입니다.",
        "transform": {
            "a": a,
            "b": b,
            "x": "roblox_origin.x + a * (easting - source_origin.easting) - b * (northing - source_origin.northing)",
            "z": "roblox_origin.z - b * (easting - source_origin.easting) - a * (northing - source_origin.northing)",
        },
        "residuals": residuals,
        "rmse_studs": rmse,
        "max_error_studs": maximum,
        "checks": {"max_error_limit_studs": max_error_studs, "threshold_status": threshold_status},
        "limitations": [
            "입력 투영좌표계와 단위의 정확성은 호출자가 확인해야 합니다.",
            "위경도 재투영, 수직 기준면 변환, 지면·수위·문턱 높이 계산은 하지 않습니다.",
            "기준점 잔차는 보정에 사용하지 않은 독립 검증점과 실제 Play 대조를 대신하지 않습니다.",
        ],
    }


def reject_constant(value: str):
    """JSON의 비표준 NaN/Infinity 리터럴을 거부한다."""
    raise AlignmentError(f"JSON에서 {value}를 사용할 수 없습니다.")


def main(argv: list[str] | None = None) -> int:
    """종료 코드 0=계산/임계 통과, 1=입력 오류, 2=임계 초과."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="미터 투영좌표 기준점 JSON 경로")
    parser.add_argument("--max-error-studs", type=float, help="기준점 최대 잔차 허용치(stud), 초과 시 종료 코드 2")
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.input.read_text(encoding="utf-8-sig"), parse_constant=reject_constant)
        result = fit_local_frame(data, args.max_error_studs)
    except (OSError, ValueError, OverflowError) as exc:
        print(f"정합 오류: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 2 if result["checks"]["threshold_status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())

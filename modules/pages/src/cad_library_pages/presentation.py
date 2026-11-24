"""Read declared expectations and published evidence for model presentation."""
import json
import math
from html import escape


def _envelope(minimum, maximum, label):
    if not all(isinstance(v, (list, tuple)) and len(v) == 3 for v in (minimum, maximum)):
        return None
    if not all(isinstance(n, (int, float)) and not isinstance(n, bool)
               and math.isfinite(n) for n in [*minimum, *maximum]):
        return None
    if any(a > b for a, b in zip(minimum, maximum)):
        return None
    return (minimum, maximum, label)


def expected_setup(owner, ci, evidence):
    """Prefer accepted baseline expected body envelopes, never actual bounds."""
    implementations = ci.get("implementations", [])
    primary = ci.get("primary")
    ordered = sorted(implementations, key=lambda row: row["id"] != primary)
    if evidence:
        for impl in ordered:
            for stage in sorted((evidence / impl["id"] / "verification").glob("*/verification.json")):
                report = json.loads(stage.read_text(encoding="utf-8"))
                for check in report.get("checks", []):
                    if check.get("id") != "baseline":
                        continue
                    envelopes = check.get("evidence", {}).get("body_envelopes", {})
                    expected = [p.get("expected", {}) for p in envelopes.get("matched_pairs", [])]
                    expected += envelopes.get("unmatched_expected", [])
                    bodies = [_envelope(b.get("min"), b.get("max"), b.get("label") or f"Body {i + 1}")
                              for i, b in enumerate(expected)]
                    if bodies and all(bodies):
                        return bodies, f"Published {impl['id']} baseline: declared expected body envelopes"
    for stage in ci.get("verifications", []):
        if stage.get("adapter") != "mesh-geometry":
            continue
        definition = owner / stage.get("definition", "")
        if not definition.is_file() or not definition.resolve().is_relative_to(owner.resolve()):
            continue
        data = json.loads(definition.read_text(encoding="utf-8"))
        body = _envelope(data.get("bounds_min"), data.get("bounds_max"), "Overall envelope")
        if body:
            return [body], f"Declared geometry requirement: {stage['definition']}"
    return [], ""


def setup_svg(bodies):
    """Conceptual front projection, not a CAD rendering or verification image."""
    if not bodies:
        return ""
    xmin = min(lo[0] for lo, _, _ in bodies)
    xmax = max(hi[0] for _, hi, _ in bodies)
    zmin = min(lo[2] for lo, _, _ in bodies)
    zmax = max(hi[2] for _, hi, _ in bodies)
    scale = min(536 / max(xmax - xmin, 1), 248 / max(zmax - zmin, 1))
    xoff = (640 - (xmax - xmin) * scale) / 2
    yoff = 76 + (248 + (zmax - zmin) * scale) / 2
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 360" role="img" aria-label="Expected setup, conceptual front projection">',
             '<rect width="640" height="360" fill="#f6f9fd"/>',
             '<text x="24" y="32" font-size="19" font-weight="600" font-family="Segoe UI, sans-serif" fill="#182235">Expected setup — front projection</text>',
             '<text x="24" y="55" font-size="13" font-family="Segoe UI, sans-serif" fill="#526279">Declared envelopes · not a geometry rendering</text>']
    for i, (lo, hi, label) in enumerate(bodies):
        x = xoff + (lo[0] - xmin) * scale
        y = yoff - (hi[2] - zmin) * scale
        w = max((hi[0] - lo[0]) * scale, 1)
        h = max((hi[2] - lo[2]) * scale, 1)
        fill, stroke = (("#dce8f5", "#46627f"), ("#e5f2ea", "#47715d"))[i % 2]
        parts.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}" fill-opacity=".65" stroke="{stroke}" stroke-width="2"/>')
        parts.append(f'<text x="{x + 5:.2f}" y="{y + 17:.2f}" font-size="12" font-family="Segoe UI, sans-serif" fill="#182235">{escape(str(label))}</text>')
    parts.append(f'<text x="24" y="345" font-size="13" font-family="Segoe UI, sans-serif" fill="#526279">Overall X: {xmax-xmin:g} mm · Z: {zmax-zmin:g} mm</text></svg>')
    return "".join(parts)


def command_sequence(path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    commands = payload.get("commands", []) if isinstance(payload, dict) else payload
    if not isinstance(commands, list):
        raise ValueError(f"invalid command sequence: {path}")
    return [{"name": str(command.get("command", "Command")),
             "json": json.dumps(command, ensure_ascii=False, indent=2)}
            for command in commands]


def implementation_evidence(root, blob_url, raw_url, state):
    """Use only artifacts actually present in this implementation's build."""
    data = {"status": state.get("status") or state.get("verification_status") or "unavailable",
            "previewurl": "", "files": [], "reports": [], "commands": [],
            "commandurl": ""}
    if (root / "model.png").is_file():
        data["previewurl"] = f"{raw_url}/model.png"
    for name, label in (("model.stl", "STL"), ("model.step", "STEP"), ("model.sc", "Native model"),
                        ("result.json", "Build result")):
        if (root / name).is_file():
            data["files"].append({"label": label, "url": f"{blob_url}/{name}"})
    path = root / "solidcraft.json"
    if path.is_file():
        data["commands"] = command_sequence(path)
        data["commandurl"] = f"{blob_url}/solidcraft.json"
    reports = sorted((root / "verification").glob("*/verification.json"))
    legacy = root / "verification/verification.json"
    if not reports and legacy.is_file():
        reports = [legacy]
    for report in reports:
        relative = report.relative_to(root).as_posix()
        data["reports"].append({"name": report.parent.name,
                                "url": f"{blob_url}/{relative}",
                                "json": json.dumps(json.loads(report.read_text(encoding="utf-8")), ensure_ascii=False, indent=2)})
    return data

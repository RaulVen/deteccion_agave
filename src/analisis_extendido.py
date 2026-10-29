from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "datasets" / "yolo26"
EVIDENCE = ROOT / "docs" / "evidencia"


def normalize_rf_name(name: str) -> str:
    return re.sub(r"_jpg\.rf\.[^.]+\.jpg$", ".jpg", name)


def read_api_key(env_file: Path | None, env_name: str) -> str | None:
    if os.environ.get(env_name):
        return os.environ[env_name]
    if env_file and env_file.exists():
        for line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            s = line.strip()
            if not s or s.startswith("#") or "=" not in s:
                continue
            key, value = s.split("=", 1)
            if key.strip() == env_name:
                return value.strip().strip("\"").strip("'")
    return None


def local_label_counts() -> dict[str, int]:
    counts = {}
    for split in ["train", "val", "test"]:
        for label_path in (DATASET / "labels" / split).glob("*.txt"):
            image_name = normalize_rf_name(label_path.with_suffix(".jpg").name)
            counts[image_name] = sum(1 for line in label_path.read_text(encoding="utf-8").splitlines() if line.strip())
    return counts


def query_project(api_key: str, workspace: str, project: str) -> dict:
    base = "https://api.roboflow.com"
    response = requests.get(f"{base}/{workspace}/{project}", params={"api_key": api_key}, timeout=30)
    response.raise_for_status()
    return response.json()


def query_version(api_key: str, workspace: str, project: str, version: str) -> dict:
    base = "https://api.roboflow.com"
    response = requests.get(f"{base}/{workspace}/{project}/{version}", params={"api_key": api_key}, timeout=30)
    response.raise_for_status()
    return response.json()


def search_images(api_key: str, workspace: str, project: str) -> list[dict]:
    base = "https://api.roboflow.com"
    records: list[dict] = []
    for offset in range(0, 5000, 250):
        body = {
            "in_dataset": True,
            "limit": 250,
            "offset": offset,
            "fields": ["name", "annotations", "split", "created"],
        }
        response = requests.post(f"{base}/{workspace}/{project}/search", params={"api_key": api_key}, json=body, timeout=45)
        response.raise_for_status()
        data = response.json()
        records.extend(data.get("results", []))
        if len(records) >= (data.get("total") or 0) or not data.get("results"):
            break
    return records


def summarize_live(records: list[dict]) -> dict:
    split_counts = {}
    class_counts = {}
    total_annotations = 0
    for record in records:
        split = record.get("split") or "unknown"
        split_counts[split] = split_counts.get(split, 0) + 1
        annotations = record.get("annotations") or {}
        count = int(annotations.get("count") or 0)
        total_annotations += count
        for cls, cls_count in (annotations.get("classes") or {}).items():
            class_counts[cls] = class_counts.get(cls, 0) + int(cls_count)
    return {
        "returned_records": len(records),
        "split_counts_returned": split_counts,
        "annotation_count_returned": total_annotations,
        "classes_returned": class_counts,
    }


def compare_local_live(records: list[dict], local: dict[str, int]) -> dict:
    live = {
        normalize_rf_name(record["name"]): int((record.get("annotations") or {}).get("count") or 0)
        for record in records
    }
    differences = []
    for name in sorted(set(live) & set(local)):
        if live[name] != local[name]:
            differences.append(
                {
                    "name": name,
                    "local_boxes": local[name],
                    "live_boxes": live[name],
                    "delta_live_minus_local": live[name] - local[name],
                }
            )
    return {
        "live_records": len(live),
        "local_records": len(local),
        "live_boxes": sum(live.values()),
        "local_boxes": sum(local.values()),
        "missing_local": sorted(set(live) - set(local)),
        "missing_live": sorted(set(local) - set(live)),
        "count_differences": differences,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default="raul-stlme")
    parser.add_argument("--project", default="agave-vty65")
    parser.add_argument("--version", default="1")
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--env-name", default="ROBOFLOW_API_KEY")
    args = parser.parse_args()

    api_key = read_api_key(args.env_file, args.env_name)
    if not api_key:
        raise SystemExit(f"Missing {args.env_name}. Set it in the environment or pass --env-file.")

    EVIDENCE.mkdir(exist_ok=True)
    project = query_project(api_key, args.workspace, args.project)
    version = query_version(api_key, args.workspace, args.project, args.version)
    records = search_images(api_key, args.workspace, args.project)
    local = local_label_counts()
    verification = {
        "workspace": args.workspace,
        "project": args.project,
        "source_url": f"https://app.roboflow.com/{args.workspace}/{args.project}/dataset",
        "verified": True,
        "project_summary": {
            key: project.get("project", {}).get(key)
            for key in ["id", "type", "name", "images", "unannotated", "annotation", "splits", "classes", "public", "versions"]
        },
        "version_summary": {
            "project_preprocessing": project.get("project", {}).get("preprocessing"),
            "project_augmentation": project.get("project", {}).get("augmentation"),
            "version": {
                key: version.get("version", {}).get(key)
                for key in ["id", "name", "images", "splits", "preprocessing", "augmentation", "model"]
            },
        },
        "search_summary": summarize_live(records),
    }
    diff = compare_local_live(records, local)
    (EVIDENCE / "roboflow_live_verification.json").write_text(json.dumps(verification, ensure_ascii=False, indent=2), encoding="utf-8")
    (EVIDENCE / "roboflow_local_label_count_diff.json").write_text(json.dumps(diff, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"project": verification["project_summary"], "search": verification["search_summary"], "diff": diff}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

from __future__ import annotations

import csv
import json
import platform
from dataclasses import asdict
from pathlib import Path

import typer

from drowsy_preprocessing import __version__
from drowsy_preprocessing.config import Settings
from drowsy_preprocessing.evaluation.annotations import read_annotations
from drowsy_preprocessing.evaluation.benchmark import benchmark as run_benchmark
from drowsy_preprocessing.evaluation.metrics import evaluate_events
from drowsy_preprocessing.signals.events import EventDetector
from drowsy_preprocessing.signals.windows import sliding_windows
from drowsy_preprocessing.sources.drozy import DrozySource, read_manifest

app = typer.Typer(no_args_is_help=True)


@app.command("inspect-dataset")
def inspect_dataset(config: Path, manifest: Path):
    source = DrozySource(Settings.load(config))
    typer.echo(json.dumps([source.audit(e) for e in read_manifest(manifest)], indent=2))


def _write_jsonl(path: Path, values):
    path.write_text(
        "".join(
            json.dumps(asdict(x), allow_nan=False, sort_keys=True) + "\n"
            for x in values
        ),
        encoding="utf-8",
    )


@app.command()
def extract(config: Path, manifest: Path, output: Path):
    settings = Settings.load(config)
    output.mkdir(parents=True, exist_ok=True)
    source = DrozySource(settings)
    all_frames = []
    all_events = []
    all_windows = []
    for entry in read_manifest(manifest):
        frames = source.load(entry)
        events = EventDetector(settings).run(frames)
        windows = sliding_windows(frames, events, settings)
        all_frames.extend(frames)
        all_events.extend(events)
        all_windows.extend(windows)
    _write_jsonl(output / "frames.jsonl", all_frames)
    _write_jsonl(output / "events.jsonl", all_events)
    (output / "windows.jsonl").write_text(
        "".join(w.to_json() + "\n" for w in all_windows), encoding="utf-8"
    )
    metadata = {
        "package_version": __version__,
        "schema_version": settings.schema_version,
        "config_hash": settings.hash,
        "python": platform.python_version(),
        "model_hashes": {},
        "input_mutated": False,
    }
    (output / "run_metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )


@app.command("annotate-export")
def annotate_export(output: Path):
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            ["session_id", "subject_id", "kind", "start_s", "end_s", "annotator_id"]
        )


@app.command()
def evaluate(annotations: Path | None = None):
    gt = (
        read_annotations(annotations) if annotations and annotations.is_file() else None
    )
    typer.echo(json.dumps(evaluate_events([], gt), indent=2))


@app.command()
def benchmark(iterations: int = 10000):
    typer.echo(json.dumps(run_benchmark(lambda x: x + 1, range(iterations)), indent=2))


if __name__ == "__main__":
    app()

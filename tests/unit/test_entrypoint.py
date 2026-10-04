from pathlib import Path


def test_python_module_entrypoint_is_packaged():
    entrypoint = (
        Path(__file__).parents[2] / "src" / "drowsy_preprocessing" / "__main__.py"
    )
    source = entrypoint.read_text(encoding="utf-8")
    assert "from drowsy_preprocessing.cli import app" in source
    assert 'if __name__ == "__main__"' in source

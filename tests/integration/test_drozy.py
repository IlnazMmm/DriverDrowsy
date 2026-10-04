import json
import pytest
from drowsy_preprocessing.config import Settings
from drowsy_preprocessing.sources.drozy import DrozySource, read_manifest


def test_length_mismatch_and_ambiguous_interp_block(tmp_path):
    (tmp_path / "t.csv").write_text("0\n1\n")
    (tmp_path / "l.json").write_text(json.dumps([[[0, 0]] * 68]))
    (tmp_path / "i.csv").write_text("0\n")
    (tmp_path / "m.csv").write_text(
        "session_id,subject_id,timestamps,landmarks,interp_indices,video,kss\ns,p,t.csv,l.json,i.csv,,\n"
    )
    entry = read_manifest(tmp_path / "m.csv")[0]
    report = DrozySource(Settings()).audit(entry)
    assert "blocking_error" in report
    with pytest.raises(ValueError):
        DrozySource(Settings()).load(entry)

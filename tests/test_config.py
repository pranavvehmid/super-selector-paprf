import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rrselect import config


def test_expected_files_listed():
    assert len(config.EXPECTED_FILES) == 6
    assert config.EXPECTED_FILES["ball_by_ball.csv"]["rows"] == 200_999

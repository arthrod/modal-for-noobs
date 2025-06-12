import pytest

def test_generate_plan_halts_on_inspection_failure(cli_runner, tmp_path):
    # Simulate missing repository directory
    missing_repo = tmp_path / "nonexistent"
    result = cli_runner.invoke(main, ["generate-plan", "--repo-dir", str(missing_repo)])
    assert result.exit_code != 0
    assert "Could not inspect repository. Plan generation halted." in result.output
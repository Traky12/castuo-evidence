from pathlib import Path

from validators.validate_dependency_exit_fixtures import validate


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures/dependency-exit"


def test_d0_and_d1_fixtures_are_fixture_only():
    for path in sorted(FIXTURES.glob("*.json")):
        assert validate(path) == []


def test_fixture_blocks_exit_verified_claim(tmp_path):
    source = FIXTURES / "D0-identity-provider-substitution.json"
    destination = tmp_path / source.name
    destination.write_text(source.read_text(encoding="utf-8").replace('"evidence_state": "FIXTURE_ONLY"', '"evidence_state": "EXIT_VERIFIED"'), encoding="utf-8")
    findings = validate(destination)
    assert any("FIXTURE_ONLY" in finding for finding in findings)

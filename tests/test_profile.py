"""Tests for loading and validating an organisation profile (organisation.yaml)."""

import logging
from collections.abc import Callable
from pathlib import Path

import pytest

from accounting_agent.profile import ProfileError, load_profile

VALID = """\
organisation: example
features:
  accounting: true
  payroll: false
"""


def test_loads_example_fixture(example_config_dir: Path) -> None:
    profile = load_profile(example_config_dir)

    assert profile.organisation == "example"
    assert profile.features == {
        "accounting": True,
        "payroll": False,
        "gmail": False,
        "discord": False,
    }


def test_enabled_and_disabled_features_are_sorted(example_config_dir: Path) -> None:
    profile = load_profile(example_config_dir)

    assert profile.enabled_features == ["accounting"]
    assert profile.disabled_features == ["discord", "gmail", "payroll"]


def test_missing_config_dir_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(ProfileError, match="does not exist"):
        load_profile(tmp_path / "missing")


def test_missing_profile_file_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(ProfileError, match="organisation.yaml"):
        load_profile(tmp_path)


def test_invalid_yaml_is_an_error(write_profile: Callable[[str], Path]) -> None:
    config_dir = write_profile("organisation: [unclosed\n")

    with pytest.raises(ProfileError, match="not valid YAML"):
        load_profile(config_dir)


def test_unsafe_yaml_tags_are_rejected(write_profile: Callable[[str], Path]) -> None:
    # Loading must never construct arbitrary Python objects from the file.
    config_dir = write_profile("organisation: !!python/object/apply:os.getcwd []\n")

    with pytest.raises(ProfileError, match="not valid YAML"):
        load_profile(config_dir)


def test_top_level_must_be_a_mapping(write_profile: Callable[[str], Path]) -> None:
    config_dir = write_profile("- organisation\n- features\n")

    with pytest.raises(ProfileError, match="mapping"):
        load_profile(config_dir)


def test_empty_file_is_an_error(write_profile: Callable[[str], Path]) -> None:
    config_dir = write_profile("")

    with pytest.raises(ProfileError, match="mapping"):
        load_profile(config_dir)


def test_missing_organisation_is_an_error(write_profile: Callable[[str], Path]) -> None:
    config_dir = write_profile("features:\n  accounting: true\n")

    with pytest.raises(ProfileError, match="'organisation'"):
        load_profile(config_dir)


@pytest.mark.parametrize("value", ["Hbg Judo", "hbg_judo", "-judo", "''", "42"])
def test_organisation_must_be_a_lowercase_slug(
    write_profile: Callable[[str], Path], value: str
) -> None:
    config_dir = write_profile(
        f"organisation: {value}\nfeatures:\n  accounting: true\n"
    )

    with pytest.raises(ProfileError, match="'organisation'"):
        load_profile(config_dir)


def test_missing_features_is_an_error(write_profile: Callable[[str], Path]) -> None:
    config_dir = write_profile("organisation: example\n")

    with pytest.raises(ProfileError, match="'features'"):
        load_profile(config_dir)


def test_features_must_be_a_mapping(write_profile: Callable[[str], Path]) -> None:
    config_dir = write_profile("organisation: example\nfeatures:\n  - accounting\n")

    with pytest.raises(ProfileError, match="'features'"):
        load_profile(config_dir)


@pytest.mark.parametrize("value", ['"true"', "1", "null"])
def test_feature_values_must_be_booleans(
    write_profile: Callable[[str], Path], value: str
) -> None:
    config_dir = write_profile(
        f"organisation: example\nfeatures:\n  payroll: {value}\n"
    )

    with pytest.raises(ProfileError, match="'payroll'"):
        load_profile(config_dir)


def test_unknown_top_level_keys_are_ignored_with_a_warning(
    write_profile: Callable[[str], Path], caplog: pytest.LogCaptureFixture
) -> None:
    # Later MVPs add sections (e.g. approval policies); an older core should not break.
    config_dir = write_profile(VALID + "approval:\n  payment: human\n")

    with caplog.at_level(logging.WARNING):
        profile = load_profile(config_dir)

    assert profile.organisation == "example"
    assert "approval" in caplog.text

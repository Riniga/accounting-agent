"""Organisation profile: which organisation a run is for and which features it uses.

The profile is read from ``organisation.yaml`` in the organisation's configuration
directory. It is the only place organisation-specific settings enter the core.
"""

import logging
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

PROFILE_FILE_NAME = "organisation.yaml"
KNOWN_KEYS = frozenset({"organisation", "features"})
# Lowercase slug, as used on the command line and in file and resource names.
ORGANISATION_ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


class ProfileError(Exception):
    """The organisation profile is missing or invalid."""


@dataclass(frozen=True)
class OrganisationProfile:
    """A validated organisation profile."""

    organisation: str
    features: dict[str, bool]

    @property
    def enabled_features(self) -> list[str]:
        """Names of enabled features, sorted."""
        return sorted(name for name, enabled in self.features.items() if enabled)

    @property
    def disabled_features(self) -> list[str]:
        """Names of disabled features, sorted."""
        return sorted(name for name, enabled in self.features.items() if not enabled)


def load_profile(config_dir: Path) -> OrganisationProfile:
    """Read and validate ``organisation.yaml`` from ``config_dir``.

    Raises:
        ProfileError: if the directory or file is missing, or the content is invalid.
    """
    if not config_dir.is_dir():
        raise ProfileError(f"Configuration directory {config_dir} does not exist.")

    path = config_dir / PROFILE_FILE_NAME
    if not path.is_file():
        raise ProfileError(f"{PROFILE_FILE_NAME} not found in {config_dir}.")

    try:
        # safe_load: the file must never be able to construct arbitrary Python objects.
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise ProfileError(f"{path} is not valid YAML: {error}") from error

    if not isinstance(data, dict):
        raise ProfileError(
            f"{path} must contain a mapping with 'organisation' and 'features'."
        )

    for key in sorted(set(data) - KNOWN_KEYS, key=str):
        logger.warning("Ignoring unknown key '%s' in %s.", key, path)

    return OrganisationProfile(
        organisation=_parse_organisation(data.get("organisation"), path),
        features=_parse_features(data.get("features"), path),
    )


def _parse_organisation(value: object, path: Path) -> str:
    if not isinstance(value, str) or not ORGANISATION_ID.fullmatch(value):
        raise ProfileError(
            f"'organisation' in {path} must be a lowercase id such as 'hbg-judo', "
            f"got {value!r}."
        )
    return value


def _parse_features(value: object, path: Path) -> dict[str, bool]:
    if not isinstance(value, dict):
        raise ProfileError(
            f"'features' in {path} must be a mapping of feature names to true/false."
        )

    features: dict[str, bool] = {}
    for name, enabled in value.items():
        # bool is checked exactly: YAML 1 or "true" must not silently count as enabled.
        if not isinstance(name, str) or not isinstance(enabled, bool):
            raise ProfileError(
                f"Feature {name!r} in {path} must be set to true or false, got {enabled!r}."
            )
        features[name] = enabled
    return features

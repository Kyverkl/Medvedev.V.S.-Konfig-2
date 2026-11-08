"""Fetch direct Cargo dependencies without cargo CLI."""

from __future__ import annotations

import json
import urllib.error
import urllib.request


class CargoError(Exception):
    """Error while fetching Cargo package data."""


CRATES_API = "https://crates.io/api/v1/crates"
HTTP_TIMEOUT_SEC = 30
USER_AGENT = "depvis-student-tool/0.1"
HTTP_NOT_FOUND = 404
KIND_NORMAL = "normal"


def fetch_direct_deps(package: str, repository: str) -> list[str]:
    """
    Return names of direct dependencies of a package.

    Uses the public crates.io HTTP API only.
    """
    _validate_package_name(package)
    _ = repository
    url = f"{CRATES_API}/{package}"
    payload = _http_get_json(url)
    return _extract_deps(payload, package)


def _validate_package_name(package: str) -> None:
    """Validate crate name characters."""
    cleaned = package.replace("-", "").replace("_", "")
    if not package or not cleaned.isalnum():
        raise CargoError(f"invalid package name: {package!r}")


def _http_get_json(url: str) -> dict:
    """HTTP GET and parse JSON body."""
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(
            request, timeout=HTTP_TIMEOUT_SEC
        ) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        if exc.code == HTTP_NOT_FOUND:
            raise CargoError(f"package not found: {url}") from exc
        raise CargoError(f"HTTP {exc.code}: {url}") from exc
    except urllib.error.URLError as exc:
        raise CargoError(f"network: {exc.reason}") from exc
    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise CargoError("API response is not JSON") from exc


def _extract_deps(payload: dict, package: str) -> list[str]:
    """Extract dependency names from crates.io payload."""
    crate = payload.get("crate") or {}
    versions = payload.get("versions") or []
    if versions:
        version_num = versions[0].get("num")
        if version_num:
            return _deps_for_version(package, version_num)
    return _deps_for_latest(package, crate)


def _deps_for_latest(package: str, crate: dict) -> list[str]:
    """Dependencies for max/newest version field."""
    version = crate.get("max_version") or crate.get("newest_version")
    if not version:
        raise CargoError(f"no version for package {package}")
    return _deps_for_version(package, version)


def _deps_for_version(package: str, version: str) -> list[str]:
    """Direct runtime dependencies of a specific version."""
    url = f"{CRATES_API}/{package}/{version}/dependencies"
    payload = _http_get_json(url)
    items = payload.get("dependencies") or []
    return _names_from_items(items)


def _names_from_items(items: list) -> list[str]:
    """Collect unique normal-kind dependency names."""
    names: list[str] = []
    for item in items:
        if not _is_normal_kind(item):
            continue
        name = item.get("crate_id") or item.get("name")
        if name and name not in names:
            names.append(name)
    return names


def _is_normal_kind(item: dict) -> bool:
    """True for runtime dependency entries."""
    kind = item.get("kind", KIND_NORMAL)
    if kind is None or kind == "":
        return True
    return kind == KIND_NORMAL

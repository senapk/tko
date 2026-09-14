"""Convert pre-profile repository configuration before normal repository loading."""
from __future__ import annotations

from tko.repository.remote import Source, SourceKeys, SourceType
from tko.repository.task_data_format import DataDict, DataValue


LEGACY_ROOT_FIELDS = frozenset({
    "sandbox_name", "sandbox_index", "sources", "flags", "lang", "audit",
    "selected", "selected_index", "pinned", "expanded",
})


def _mapping(value: DataValue, field: str) -> DataDict:
    if not isinstance(value, dict):
        raise ValueError(f"Expected a table for {field}")
    return value.copy()


def _legacy_sources(value: DataValue) -> tuple[DataDict, list[str]]:
    if not isinstance(value, list):
        raise ValueError("Expected a list of legacy sources")
    sources: DataDict = {}
    editable: list[str] = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError("Invalid legacy source")
        source: Source = Source.from_dict(item)
        if not source.name or not source.path_or_url or source.name in sources:
            raise ValueError("Invalid or duplicate legacy source")
        sources[source.name] = {"uri": source.path_or_url}
        if item.get(SourceKeys.TYPE) == SourceType.LOCAL_FILE.value and item.get(SourceKeys.WRITEABLE) is True:
            editable.append(source.name)
    return sources, editable


def canonical_repository_config(data: DataDict) -> DataDict:
    """Keep unrelated fields while moving known legacy fields to their current tables."""
    output: DataDict = data.copy()
    profile_value: DataValue = output.get("profile", {})
    profile: DataDict = _mapping(profile_value, "profile")
    if "audit" in profile:
        profile["audit"] = {
            key: value for key, value in _mapping(profile["audit"], "profile.audit").items()
            if key != "interval_seconds" or value is not None
        }
    preferences_value: DataValue = output.get("preferences", {})
    preferences: DataDict = _mapping(preferences_value, "preferences")
    state_value: DataValue = output.get("state", {})
    state: DataDict = _mapping(state_value, "state")

    legacy_sources: DataValue = output.get("sources")
    editable: list[str] = []
    if "sources" in output:
        sources, editable = _legacy_sources(legacy_sources)
        profile["sources"] = sources
    sandbox: DataValue = output.get("sandbox_name")
    sandbox_index: DataValue = output.get("sandbox_index")
    if "sandbox_name" in output:
        if not isinstance(sandbox, str) or not sandbox:
            raise ValueError("Invalid sandbox_name")
        profile["authoring_source"] = sandbox
        sources_value: DataValue = profile.get("sources", {})
        sources = _mapping(sources_value, "profile.sources")
        if isinstance(sandbox_index, str) and sandbox_index:
            sources[sandbox] = {"uri": sandbox_index}
        elif sandbox not in sources:
            raise ValueError("Missing sandbox_index and sandbox source")
        profile["sources"] = sources
    elif "sources" in output and "authoring_source" not in profile:
        if len(editable) != 1:
            raise ValueError("Cannot infer authoring source from legacy sources")
        profile["authoring_source"] = editable[0]

    if "audit" in output:
        audit: DataDict = _mapping(output["audit"], "audit")
        # TOML has no null. The current loader interprets a missing interval as None.
        audit = {key: value for key, value in audit.items() if key != "interval_seconds" or value is not None}
        profile["audit"] = audit
    if "flags" in output:
        preferences.update(_mapping(output["flags"], "flags"))
    if "lang" in output:
        language: DataValue = output["lang"]
        if not isinstance(language, str):
            raise ValueError("Invalid language")
        preferences["lang"] = language
    for field in ("selected", "selected_index", "pinned", "expanded"):
        if field in output:
            state[field] = output[field]

    for field in LEGACY_ROOT_FIELDS:
        output.pop(field, None)
    version: DataValue = output.get("version")
    if version is None or version in ("0.1", "0.2"):
        output["version"] = "0.3"
    if profile:
        output["profile"] = profile
    if preferences:
        output["preferences"] = preferences
    if state:
        output["state"] = state
    return output

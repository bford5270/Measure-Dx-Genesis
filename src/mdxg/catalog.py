"""Loader for catalog/triggers.yaml and catalog/dyads.yaml.

The YAML is the specification of record. Rule implementations read their
parameters from it, so tuning a window means editing the catalog rather than
the code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .valuesets import ValueSet


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


DEFAULT_CATALOG_DIR = _repo_root() / "catalog"


@dataclass
class TriggerSpec:
    id: str
    name: str
    tier: int
    priority: str
    signal: str = ""
    look_back_days: Any = None
    look_fwd_days: Any = None
    exclusions: list[str] = field(default_factory=list)
    sample_rate: float | None = None
    needs_access: bool = True
    raw: dict = field(default_factory=dict)

    @property
    def look_back(self) -> int | None:
        v = self.look_back_days
        return int(v) if isinstance(v, (int, float)) else None


@dataclass
class DyadSpec:
    id: str
    target: str
    tier: str
    window_days: int
    target_codes: tuple[str, ...]
    symptom_codes: tuple[str, ...]
    typical_mislabel: tuple[str, ...] = ()
    symptom_presentation: str = ""
    exposure_restriction: str | None = None
    review_rule: str | None = None
    pilot_priority: int | None = None
    raw: dict = field(default_factory=dict)

    @property
    def target_set(self) -> ValueSet:
        return ValueSet(self.target_codes, name=f"{self.id}:target")

    @property
    def symptom_set(self) -> ValueSet:
        """Explicit anchors if the catalog supplies them, else empty.

        An empty symptom set means the rule falls back to the generic
        nonspecific-code definition, which is the honest default until the set
        has been calibrated locally.
        """
        return ValueSet(self.symptom_codes, name=f"{self.id}:symptom")


@dataclass
class Catalog:
    triggers: dict[str, TriggerSpec]
    dyads: dict[str, DyadSpec]

    def trigger(self, tid: str) -> TriggerSpec:
        return self.triggers[tid]

    def dyads_for_pilot(self) -> list[DyadSpec]:
        pilot = self._pilot_ids or []
        ordered = [self.dyads[d] for d in pilot if d in self.dyads]
        return ordered or list(self.dyads.values())

    _pilot_ids: tuple[str, ...] = ()


def _as_tuple(value) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    return tuple(str(v) for v in value)


def load_catalog(directory: str | Path | None = None) -> Catalog:
    base = Path(directory) if directory else DEFAULT_CATALOG_DIR
    triggers = _load_triggers(base / "triggers.yaml")
    dyads, pilot = _load_dyads(base / "dyads.yaml")
    cat = Catalog(triggers=triggers, dyads=dyads)
    cat._pilot_ids = pilot
    return cat


def _load_triggers(path: Path) -> dict[str, TriggerSpec]:
    doc = yaml.safe_load(path.read_text())
    out: dict[str, TriggerSpec] = {}
    for tier in doc.get("tiers", []):
        tier_no = int(tier.get("tier"))
        for t in tier.get("triggers", []):
            spec = TriggerSpec(
                id=t["id"],
                name=t.get("name", ""),
                tier=tier_no,
                priority=str(t.get("priority", "medium")),
                signal=str(t.get("signal", "")),
                look_back_days=t.get("look_back_days"),
                look_fwd_days=t.get("look_fwd_days"),
                exclusions=list(t.get("exclusions", []) or []),
                sample_rate=t.get("sample_rate"),
                needs_access=bool(t.get("needs_access", True)),
                raw=t,
            )
            out[spec.id] = spec
    return out


def _load_dyads(path: Path) -> tuple[dict[str, DyadSpec], tuple[str, ...]]:
    doc = yaml.safe_load(path.read_text())
    out: dict[str, DyadSpec] = {}
    for tier in doc.get("tiers", []):
        tier_name = str(tier.get("tier"))
        for d in tier.get("dyads", []):
            targets = _as_tuple(d.get("target_codes")) or _as_tuple(
                d.get("target_codes_anchor")
            )
            spec = DyadSpec(
                id=d["id"],
                target=d.get("target", ""),
                tier=tier_name,
                window_days=int(d.get("window_days") or 0),
                target_codes=targets,
                symptom_codes=_as_tuple(d.get("symptom_codes_anchor")),
                typical_mislabel=_as_tuple(d.get("typical_mislabel")),
                symptom_presentation=str(d.get("symptom_presentation", "")),
                exposure_restriction=d.get("exposure_restriction"),
                review_rule=d.get("review_rule"),
                pilot_priority=d.get("pilot_priority"),
                raw=d,
            )
            out[spec.id] = spec
    pilot = _as_tuple((doc.get("pilot_set") or {}).get("dyads"))
    return out, pilot

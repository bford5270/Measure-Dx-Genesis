"""FHIR R4 adapter.

**Unverified against MHS GENESIS.** This follows the standard FHIR R4 resource
and search-parameter names, which are stable and public, and the Oracle
Health/Cerner Millennium conventions for identifier types. It has been exercised
against synthetic Bundles only. Before pointing it at a live endpoint you need,
at minimum: an authorized client registration, the correct base URL and tenant,
scopes for the resources below, and written authority to extract PHI for a
quality assurance purpose. None of that is a code problem.

Read-only by construction: no method here issues anything but GET.

Resource mapping:
    Encounter          -> encounters   (FIN from the identifier of type FN/VN)
    Condition          -> diagnoses
    ServiceRequest     -> orders, referrals
    Observation        -> results
    Patient            -> roster
"""

from __future__ import annotations

import time
from collections.abc import Iterator
from typing import Any

import pandas as pd
import requests

from ..model import Dataset, coerce

# Identifier type codes Millennium commonly uses for the encounter number.
FIN_TYPE_CODES = {"FN", "VN", "AN"}
MRN_TYPE_CODES = {"MR"}


class FHIRClient:
    """Minimal read-only FHIR R4 client with pagination and backoff."""

    def __init__(
        self,
        base_url: str,
        *,
        token: str | None = None,
        timeout: int = 60,
        page_size: int = 200,
        max_pages: int = 500,
        session: requests.Session | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.page_size = page_size
        self.max_pages = max_pages
        self.session = session or requests.Session()
        self.session.headers.update({"Accept": "application/fhir+json"})
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def search(self, resource: str, **params) -> Iterator[dict]:
        params.setdefault("_count", self.page_size)
        url = f"{self.base_url}/{resource}"
        pages = 0
        while url and pages < self.max_pages:
            bundle = self._get(url, params if pages == 0 else None)
            for entry in bundle.get("entry", []) or []:
                res = entry.get("resource")
                if res:
                    yield res
            url = _next_link(bundle)
            pages += 1

    def _get(self, url: str, params: dict | None) -> dict:
        for attempt in range(4):
            resp = self.session.get(url, params=params, timeout=self.timeout)
            if resp.status_code in (429, 502, 503, 504):
                time.sleep(2**attempt)
                continue
            resp.raise_for_status()
            return resp.json()
        resp.raise_for_status()
        return {}


def _next_link(bundle: dict) -> str | None:
    for link in bundle.get("link", []) or []:
        if link.get("relation") == "next":
            return link.get("url")
    return None


# --------------------------------------------------------------------------
# extraction helpers
# --------------------------------------------------------------------------


def _identifier(resource: dict, type_codes: set[str]) -> str | None:
    for ident in resource.get("identifier", []) or []:
        for coding in (ident.get("type", {}) or {}).get("coding", []) or []:
            if coding.get("code") in type_codes:
                return ident.get("value")
    return None


def _ref_id(resource: dict, key: str) -> str | None:
    ref = (resource.get(key) or {}).get("reference")
    return ref.split("/")[-1] if ref else None


def _code(resource: dict, key: str = "code", system_hint: str = "icd-10") -> str | None:
    codings = (resource.get(key) or {}).get("coding", []) or []
    for c in codings:
        if system_hint in str(c.get("system", "")).lower():
            return c.get("code")
    return codings[0].get("code") if codings else None


ENC_CLASS_MAP = {
    "AMB": "AMB", "EMER": "EMER", "IMP": "IMP", "ACUTE": "IMP",
    "VR": "VIRT", "SS": "AMB", "OBSENC": "IMP", "PRENC": "AMB",
}


def encounters_from_bundle(resources: list[dict]) -> pd.DataFrame:
    rows = []
    for r in resources:
        if r.get("resourceType") != "Encounter":
            continue
        period = r.get("period") or {}
        cls = (r.get("class") or {}).get("code")
        rows.append(
            {
                "fin": _identifier(r, FIN_TYPE_CODES) or r.get("id"),
                "mrn": _ref_id(r, "subject"),
                "start": period.get("start"),
                "end": period.get("end"),
                "enc_class": ENC_CLASS_MAP.get(str(cls).upper(), cls),
                "role_of_care": None,
                "setting": None,
                "facility": (r.get("serviceProvider") or {}).get("display"),
                "provider_id": _first_participant(r),
                "unit_id": None,
                "disposition": ((r.get("hospitalization") or {}).get("dischargeDisposition") or {}).get("text"),
            }
        )
    return coerce("encounters", pd.DataFrame(rows))


def _first_participant(enc: dict) -> str | None:
    for p in enc.get("participant", []) or []:
        ref = (p.get("individual") or {}).get("reference")
        if ref:
            return ref.split("/")[-1]
    return None


def conditions_from_bundle(resources: list[dict], enc_fin: dict[str, str]) -> pd.DataFrame:
    rows = []
    for r in resources:
        if r.get("resourceType") != "Condition":
            continue
        enc_id = _ref_id(r, "encounter")
        rows.append(
            {
                "fin": enc_fin.get(enc_id, enc_id),
                "mrn": _ref_id(r, "subject"),
                "code": _code(r),
                "system": "ICD10CM",
                "rank": _condition_rank(r),
                "date": r.get("recordedDate") or r.get("onsetDateTime"),
            }
        )
    return coerce("diagnoses", pd.DataFrame(rows))


def _condition_rank(cond: dict) -> str:
    for cat in cond.get("category", []) or []:
        for c in cat.get("coding", []) or []:
            if str(c.get("code", "")).lower() in {"chief-complaint", "problem-list-item"}:
                return "PRINCIPAL"
    return "SECONDARY"


def observations_from_bundle(resources: list[dict], enc_fin: dict[str, str]) -> pd.DataFrame:
    rows = []
    for r in resources:
        if r.get("resourceType") != "Observation":
            continue
        enc_id = _ref_id(r, "encounter")
        vq = r.get("valueQuantity") or {}
        rows.append(
            {
                "result_id": r.get("id"),
                "order_id": _ref_id(r, "basedOn") or _based_on_id(r),
                "fin": enc_fin.get(enc_id, enc_id),
                "mrn": _ref_id(r, "subject"),
                "code": _code(r, "code", system_hint="loinc"),
                "name": (r.get("code") or {}).get("text"),
                "value_num": vq.get("value"),
                "value_text": r.get("valueString"),
                "units": vq.get("unit"),
                "abnormal_flag": _interpretation(r),
                "resulted_dt": r.get("issued") or r.get("effectiveDateTime"),
                "ack_dt": None,  # not represented in core FHIR; source-specific
                "ack_provider_id": None,
            }
        )
    return coerce("results", pd.DataFrame(rows))


def _based_on_id(obs: dict) -> str | None:
    for b in obs.get("basedOn", []) or []:
        ref = b.get("reference")
        if ref:
            return ref.split("/")[-1]
    return None


def _interpretation(obs: dict) -> str:
    for interp in obs.get("interpretation", []) or []:
        for c in interp.get("coding", []) or []:
            code = str(c.get("code", "")).upper()
            if code in {"HH", "LL", "AA", "CRIT"}:
                return "AA"
            if code in {"H", "L", "A", "ABN"}:
                return "A"
    return "N"


def service_requests_from_bundle(
    resources: list[dict], enc_fin: dict[str, str]
) -> tuple[pd.DataFrame, pd.DataFrame]:
    orders, referrals = [], []
    for r in resources:
        if r.get("resourceType") != "ServiceRequest":
            continue
        enc_id = _ref_id(r, "encounter")
        fin = enc_fin.get(enc_id, enc_id)
        intent = str(r.get("intent", "")).lower()
        is_referral = intent == "order" and bool(r.get("performerType")) or intent == "plan"
        common = {
            "fin": fin,
            "mrn": _ref_id(r, "subject"),
            "ordered_dt": r.get("authoredOn"),
            "status": str(r.get("status", "")).upper(),
        }
        if is_referral:
            referrals.append(
                {
                    "referral_id": r.get("id"),
                    "specialty": ((r.get("performerType") or {}).get("text")),
                    "completed_dt": None,
                    **common,
                }
            )
        else:
            orders.append(
                {
                    "order_id": r.get("id"),
                    "category": _order_category(r),
                    "code": _code(r, "code", system_hint="loinc"),
                    "name": (r.get("code") or {}).get("text"),
                    "specialty": None,
                    "provider_id": _ref_id(r, "requester"),
                    **common,
                }
            )
    return (
        coerce("orders", pd.DataFrame(orders)),
        coerce("referrals", pd.DataFrame(referrals)),
    )


def _order_category(sr: dict) -> str:
    for cat in sr.get("category", []) or []:
        text = str(cat.get("text", "")).lower()
        if "lab" in text:
            return "LAB"
        if "imag" in text or "radiol" in text:
            return "IMG"
        if "referral" in text:
            return "REFERRAL"
    return "PROC"


def build_dataset(resources: list[dict]) -> Dataset:
    """Assemble a Dataset from a flat list of FHIR resources.

    Accepts anything: a saved Bundle's entries, several Bundles concatenated, or
    the output of repeated FHIRClient.search calls.
    """
    encounters = encounters_from_bundle(resources)
    enc_fin = {}
    for r in resources:
        if r.get("resourceType") == "Encounter":
            enc_fin[r.get("id")] = _identifier(r, FIN_TYPE_CODES) or r.get("id")

    orders, referrals = service_requests_from_bundle(resources, enc_fin)
    return Dataset(
        tables={
            "encounters": encounters,
            "diagnoses": conditions_from_bundle(resources, enc_fin),
            "results": observations_from_bundle(resources, enc_fin),
            "orders": orders,
            "referrals": referrals,
        }
    )


def pull(
    client: FHIRClient, *, patient_ids: list[str], logger=None
) -> Dataset:
    """Pull the resource set for a list of patients.

    Patient-by-patient rather than population-level because that is what a
    normal (non-bulk) FHIR authorization grants. For anything at division scale
    you want Bulk Data export or a warehouse extract, not this - see
    docs/08-data-sources.md.
    """
    resources: list[dict] = []
    for pid in patient_ids:
        for rtype, params in (
            ("Encounter", {"patient": pid}),
            ("Condition", {"patient": pid}),
            ("Observation", {"patient": pid, "category": "laboratory"}),
            ("ServiceRequest", {"patient": pid}),
        ):
            try:
                resources.extend(client.search(rtype, **params))
            except requests.HTTPError as exc:
                if logger:
                    logger.error("%s pull failed (status %s)", rtype, exc.response.status_code if exc.response else "?")
        if logger:
            logger.info("pulled patient %d of %d", patient_ids.index(pid) + 1, len(patient_ids))
    return build_dataset(resources)

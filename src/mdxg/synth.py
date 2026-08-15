"""Synthetic data generator.

Lets the whole pipeline run and be tested today, with no access to MHS GENESIS
and no PHI anywhere near it. Generates background noise plus a known number of
planted cases per trigger, so trigger recall can be verified against ground
truth before the code is ever pointed at real data.

This is not a simulation of Marine Corps epidemiology. It exists to exercise
the code paths.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .model import Dataset, coerce

BENIGN_DX = [
    "J06.9", "M54.50", "M25.561", "R10.9", "L03.115", "J02.9",
    "S93.401A", "R51.9", "K21.9", "F43.23", "M79.605", "R05.9",
]
UNITS = ["1/7", "2/7", "3/7", "1/4", "CLB-7", "HQ"]
PROVIDERS = [f"PRV{i:03d}" for i in range(1, 13)]


class SyntheticBuilder:
    def __init__(self, seed: int = 20260815, start: str = "2024-01-01"):
        self.rng = np.random.default_rng(seed)
        self.start = pd.Timestamp(start)
        self.enc: list[dict] = []
        self.dx: list[dict] = []
        self.orders: list[dict] = []
        self.results: list[dict] = []
        self.referrals: list[dict] = []
        self.disp: list[dict] = []
        self.roster: list[dict] = []
        self.assign: list[dict] = []
        self.moves: list[dict] = []
        self._n = 0
        self.planted: dict[str, list[str]] = {}

    # -- primitives ------------------------------------------------------

    def _fin(self) -> str:
        self._n += 1
        return f"F{self._n:07d}"

    def _day(self, offset: int) -> pd.Timestamp:
        return self.start + pd.Timedelta(days=int(offset))

    def encounter(
        self, mrn, day, code, *, enc_class="AMB", role="R1", setting="GARRISON",
        unit="1/7", provider=None, rank="PRINCIPAL",
    ) -> str:
        fin = self._fin()
        d = self._day(day)
        self.enc.append(
            {
                "fin": fin, "mrn": mrn, "start": d, "end": d,
                "enc_class": enc_class, "role_of_care": role, "setting": setting,
                "facility": "BAS" if role == "R1" else "MTF",
                "provider_id": provider or PROVIDERS[self.rng.integers(0, len(PROVIDERS))],
                "unit_id": unit, "disposition": "ROUTINE",
            }
        )
        if code:
            self.dx.append(
                {"fin": fin, "mrn": mrn, "code": code, "system": "ICD10CM",
                 "rank": rank, "date": d}
            )
        return fin

    def disposition(self, mrn, day, kind, code=None, fin=None) -> None:
        self.disp.append(
            {"mrn": mrn, "kind": kind, "effective_date": self._day(day),
             "code": code, "detail": None, "fin": fin}
        )

    def _plant(self, trigger: str, fin: str) -> str:
        self.planted.setdefault(trigger, []).append(fin)
        return fin

    # -- population ------------------------------------------------------

    def background(self, n_marines: int = 300, visits_per_marine: int = 3) -> None:
        for i in range(n_marines):
            mrn = f"M{i:06d}"
            unit = UNITS[int(self.rng.integers(0, len(UNITS)))]
            self.roster.append(
                {"mrn": mrn, "birth_date": pd.Timestamp("2003-01-01"),
                 "sex": "M" if i % 6 else "F", "unit_id": unit,
                 "gain_date": self.start, "loss_date": pd.NaT}
            )
            for _ in range(int(self.rng.poisson(visits_per_marine)) + 1):
                self.encounter(
                    mrn,
                    int(self.rng.integers(0, 500)),
                    BENIGN_DX[int(self.rng.integers(0, len(BENIGN_DX)))],
                    unit=unit,
                )

        for p in PROVIDERS:
            self.assign.append(
                {"provider_id": p, "unit_id": UNITS[0],
                 "start_date": self.start, "end_date": pd.NaT}
            )

    # -- planted cases ---------------------------------------------------

    def plant_dyad_stress_fracture(self, mrn="M900001") -> None:
        """Thigh pain labelled strain, then a femoral stress fracture (D-B01)."""
        self._roster(mrn)
        f = self.encounter(mrn, 100, "M79.605")  # limb pain, unspecified
        self._plant("T-10", f)
        self.encounter(mrn, 130, "M79.605")
        self.encounter(mrn, 160, "M84.359A", enc_class="AMB", role="MTF")

    def plant_dyad_torsion(self, mrn="M900002") -> None:
        """Groin pain, then torsion within 7 days (D-A01)."""
        self._roster(mrn)
        f = self.encounter(mrn, 200, "R10.2")
        self._plant("T-10", f)
        fin = self.encounter(mrn, 204, "N44.00", enc_class="EMER", role="MTF")
        self.disposition(mrn, 204, "SURGERY_EMERGENT", "N44.00", fin)
        self._plant("T-05", f)

    def plant_rule_of_three(self, mrn="M900003") -> None:
        a = self.encounter(mrn, 50, "R10.9")
        self._roster(mrn)
        self._plant("T-06", a)
        self.encounter(mrn, 60, "R10.31")
        self.encounter(mrn, 70, "R10.32", enc_class="EMER", role="MTF")

    def plant_unplanned_admission(self, mrn="M900004") -> None:
        self._roster(mrn)
        f = self.encounter(mrn, 300, "R07.9")
        self._plant("T-07", f)
        self.encounter(mrn, 306, "R07.2", enc_class="IMP", role="MTF")

    def plant_icu_escalation(self, mrn="M900005") -> None:
        self._roster(mrn)
        f = self.encounter(mrn, 120, "B34.9")
        self._plant("T-02", f)
        fin = self.encounter(mrn, 126, "A41.9", enc_class="IMP", role="MTF")
        self.disposition(mrn, 126, "ICU", "A41.9", fin)

    def plant_death(self, mrn="M900006") -> None:
        self._roster(mrn)
        f = self.encounter(mrn, 210, "R53.83")
        self._plant("T-01", f)
        self.disposition(mrn, 300, "DEATH", "I46.9")

    def plant_limdu(self, mrn="M900007") -> None:
        self._roster(mrn)
        f = self.encounter(mrn, 20, "M54.50")
        self._plant("T-11", f)
        self.encounter(mrn, 200, "M54.50")
        self.disposition(mrn, 250, "LIMDU", "M54.50")

    def plant_unacked_result(self, mrn="M900008", day: int = 400) -> None:
        self._roster(mrn)
        fin = self.encounter(mrn, day, "Z00.00")
        self._plant("T-16", fin)
        self.orders.append(
            {"order_id": "O900008", "fin": fin, "mrn": mrn, "category": "LAB",
             "code": "58410-2", "name": "CBC", "specialty": None,
             "ordered_dt": self._day(day), "status": "COMPLETED",
             "provider_id": PROVIDERS[0]}
        )
        self.results.append(
            {"result_id": "R900008", "order_id": "O900008", "fin": fin, "mrn": mrn,
             "code": "718-7", "name": "Hemoglobin", "value_num": 8.4,
             "value_text": None, "units": "g/dL", "abnormal_flag": "AA",
             "resulted_dt": self._day(day + 1), "ack_dt": pd.NaT,
             "ack_provider_id": None}
        )

    def plant_open_referral(self, mrn="M900009", day: int = 380) -> None:
        self._roster(mrn)
        fin = self.encounter(mrn, day, "N50.819")
        self._plant("T-17", fin)
        self.referrals.append(
            {"referral_id": "REF900009", "fin": fin, "mrn": mrn,
             "specialty": "Urology", "ordered_dt": self._day(day),
             "completed_dt": pd.NaT, "status": "ORDERED"}
        )

    def plant_pending_at_movement(self, mrn="M900010", day: int = 330) -> None:
        self._roster(mrn, unit="2/7")
        fin = self.encounter(mrn, day, "R07.9", unit="2/7")
        self._plant("T-19", fin)
        self.orders.append(
            {"order_id": "O900010", "fin": fin, "mrn": mrn, "category": "IMG",
             "code": "71046", "name": "Chest imaging", "specialty": None,
             "ordered_dt": self._day(day), "status": "ORDERED",
             "provider_id": PROVIDERS[1]}
        )
        self.moves.append(
            {"unit_id": "2/7", "kind": "DEPLOYMENT",
             "start_date": self._day(day + 10), "end_date": self._day(day + 200)}
        )

    def plant_orphan_result(self, mrn="M900011", day: int = 340) -> None:
        self._roster(mrn)
        fin = self.encounter(mrn, day, "R10.9", provider="PRV099")
        self._plant("T-20", fin)
        self.assign.append(
            {"provider_id": "PRV099", "unit_id": UNITS[0],
             "start_date": self.start, "end_date": self._day(day + 5)}
        )
        self.orders.append(
            {"order_id": "O900011", "fin": fin, "mrn": mrn, "category": "LAB",
             "code": "24357-6", "name": "Urinalysis", "specialty": None,
             "ordered_dt": self._day(day), "status": "COMPLETED",
             "provider_id": "PRV099"}
        )
        self.results.append(
            {"result_id": "R900011", "order_id": "O900011", "fin": fin, "mrn": mrn,
             "code": "24357-6", "name": "Urinalysis", "value_num": None,
             "value_text": None, "units": None, "abnormal_flag": "A",
             "resulted_dt": self._day(day + 12), "ack_dt": pd.NaT,
             "ack_provider_id": None}
        )

    def _roster(self, mrn: str, unit: str = "1/7") -> None:
        if any(r["mrn"] == mrn for r in self.roster):
            return
        self.roster.append(
            {"mrn": mrn, "birth_date": pd.Timestamp("2003-01-01"), "sex": "M",
             "unit_id": unit, "gain_date": self.start, "loss_date": pd.NaT}
        )

    # -- build -----------------------------------------------------------

    def build(self) -> Dataset:
        tables = {
            "encounters": coerce("encounters", pd.DataFrame(self.enc)),
            "diagnoses": coerce("diagnoses", pd.DataFrame(self.dx)),
            "orders": coerce("orders", pd.DataFrame(self.orders)),
            "results": coerce("results", pd.DataFrame(self.results)),
            "referrals": coerce("referrals", pd.DataFrame(self.referrals)),
            "dispositions": coerce("dispositions", pd.DataFrame(self.disp)),
            "roster": coerce("roster", pd.DataFrame(self.roster)),
            "provider_assignments": coerce("provider_assignments", pd.DataFrame(self.assign)),
            "unit_movements": coerce("unit_movements", pd.DataFrame(self.moves)),
        }
        ds = Dataset(tables=tables)
        ds.planted = self.planted  # type: ignore[attr-defined]
        return ds


def build_demo(seed: int = 20260815, n_marines: int = 300) -> Dataset:
    """A dataset containing background noise plus one planted case per trigger."""
    b = SyntheticBuilder(seed=seed)
    b.background(n_marines=n_marines)
    b.plant_dyad_stress_fracture()
    b.plant_dyad_torsion()
    b.plant_rule_of_three()
    b.plant_unplanned_admission()
    b.plant_icu_escalation()
    b.plant_death()
    b.plant_limdu()
    b.plant_unacked_result()
    b.plant_open_referral()
    b.plant_pending_at_movement()
    b.plant_orphan_result()
    return b.build()

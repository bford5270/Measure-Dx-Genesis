"""Episode packet assembly.

Measure Dx is explicit that the unit of review is the episode, not the note. A
reviewer handed a single encounter cannot score the Revised Safer Dx Instrument
honestly, because items 9, 11 and 12 all require the trajectory.

`build_packet` assembles everything in the look-back window for one FIN.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .model import Dataset


@dataclass
class Packet:
    fin: str
    mrn: str
    window_start: pd.Timestamp
    window_end: pd.Timestamp
    encounters: pd.DataFrame
    diagnoses: pd.DataFrame
    orders: pd.DataFrame
    results: pd.DataFrame
    referrals: pd.DataFrame
    dispositions: pd.DataFrame

    @property
    def complete(self) -> bool:
        """Whether the packet has enough to adjudicate.

        Incomplete packets are deferred, not adjudicated on a fragment - see
        docs/06-review-process.md.
        """
        return not self.encounters.empty and not self.diagnoses.empty

    def to_text(self) -> str:
        """A readable chronology for the reviewer."""
        lines = [
            f"EPISODE PACKET - index FIN {self.fin}",
            f"Window: {self.window_start:%Y-%m-%d} to {self.window_end:%Y-%m-%d}",
            f"Encounters in window: {len(self.encounters)}",
            "",
            "CHRONOLOGY",
        ]
        dx_by_fin = self.diagnoses.groupby("fin")["code"].apply(
            lambda s: ", ".join(str(x) for x in s.dropna().unique())
        )
        for _, e in self.encounters.sort_values("start").iterrows():
            marker = " <== INDEX" if e["fin"] == self.fin else ""
            codes = dx_by_fin.get(e["fin"], "")
            lines.append(
                f"  {e['start']:%Y-%m-%d}  {str(e['enc_class']):5s} "
                f"{str(e['role_of_care'] or ''):9s} FIN {e['fin']}  {codes}{marker}"
            )

        if not self.results.empty:
            lines += ["", "RESULTS"]
            for _, r in self.results.sort_values("resulted_dt").iterrows():
                ack = "acknowledged" if pd.notna(r["ack_dt"]) else "NOT ACKNOWLEDGED"
                lines.append(
                    f"  {r['resulted_dt']:%Y-%m-%d}  {str(r['code'] or '')}  "
                    f"flag={r['abnormal_flag']}  {ack}"
                )

        if not self.referrals.empty:
            lines += ["", "REFERRALS"]
            for _, r in self.referrals.sort_values("ordered_dt").iterrows():
                done = (
                    f"completed {r['completed_dt']:%Y-%m-%d}"
                    if pd.notna(r["completed_dt"])
                    else "NOT COMPLETED"
                )
                lines.append(
                    f"  {r['ordered_dt']:%Y-%m-%d}  {str(r['specialty'] or '')}  {done}"
                )

        if not self.dispositions.empty:
            lines += ["", "DISPOSITIONS"]
            for _, d in self.dispositions.sort_values("effective_date").iterrows():
                lines.append(
                    f"  {d['effective_date']:%Y-%m-%d}  {d['kind']}  {str(d['code'] or '')}"
                )

        lines += [
            "",
            "Score with the Revised Safer Dx Instrument (13 items). Judge on the",
            "information available to the clinician at the time. A case that escalated",
            "because a correctly and timely diagnosed condition progressed is not a",
            "missed opportunity - use the dedicated field.",
        ]
        return "\n".join(lines)


def build_packet(
    ds: Dataset, fin: str, *, look_back_days: int = 180, look_forward_days: int = 90
) -> Packet:
    enc_all = ds.get("encounters")
    row = enc_all[enc_all["fin"] == fin]
    if row.empty:
        raise KeyError(f"fin {fin!r} not found in encounters")
    idx = row.iloc[0]
    mrn = idx["mrn"]
    start = idx["start"] - pd.Timedelta(days=look_back_days)
    end = idx["start"] + pd.Timedelta(days=look_forward_days)

    def _win(df, col):
        if df.empty:
            return df
        sub = df[df["mrn"] == mrn] if "mrn" in df.columns else df
        if sub.empty or col not in sub.columns:
            return sub
        return sub[(sub[col] >= start) & (sub[col] <= end)].sort_values(col)

    encs = _win(enc_all, "start")
    fins = set(encs["fin"])

    dx = ds.get("diagnoses")
    dx = dx[dx["fin"].isin(fins)] if not dx.empty else dx

    return Packet(
        fin=fin,
        mrn=mrn,
        window_start=start,
        window_end=end,
        encounters=encs,
        diagnoses=dx,
        orders=_win(ds.get("orders"), "ordered_dt"),
        results=_win(ds.get("results"), "resulted_dt"),
        referrals=_win(ds.get("referrals"), "ordered_dt"),
        dispositions=_win(ds.get("dispositions"), "effective_date"),
    )

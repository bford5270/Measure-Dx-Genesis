"""mdxg - diagnostic safety case finding for USMC operational forces.

Reads a medical record extract, applies the trigger catalog in ``catalog/``, and
returns a FIN-keyed worklist of notes that may benefit from structured review.

A trigger firing is a question, not a finding. Adjudication is a clinician task
performed with the Revised Safer Dx Instrument. Nothing in this package writes
to the source system, and nothing in it determines that care was substandard.

Before running against live data, read docs/11-running-the-code.md - the
compliance gate is not optional and is not a code problem.
"""

from .catalog import load_catalog
from .model import Dataset, coerce, validate

__version__ = "0.1.0"

__all__ = ["Dataset", "coerce", "validate", "load_catalog", "__version__"]

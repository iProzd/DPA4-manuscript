"""
Recompute Matbench Discovery leaderboard metrics for the DPA4 model family.

Classification metrics follow the reference pipeline exactly: predictions are
aligned with the WBM summary table, rounded to 3 decimals, restricted to the
unique-prototype subset, and converted to convex-hull distances via

    each_pred = each_true + e_form_pred - e_form_dft.

The regression metrics (MAE, RMSE, R2) are reported both over the full subset and
with relaxation failures excluded. A structure counts as a failure when its
absolute hull-distance error exceeds `error_cutoff`; such deviations are orders of
magnitude beyond any physical formation-energy scale and dominate the sums of
squares, which otherwise renders R2 meaningless.

Usage
-----
python scripts/matbench_metrics.py --root ~/Downloads/Matbench_Test/Final
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

RMSD_BASELINE = 0.15
STABILITY_THRESHOLD = 0.0


@dataclass(frozen=True)
class ModelRun:
    """One evaluated checkpoint and the artifacts describing it."""

    name: str
    preds_csv: Path
    stats_json: Path
    kappa_txt: Path
    params_m: float


def discover_runs(root: Path, params: dict[str, float]) -> list[ModelRun]:
    """
    Collect the artifact paths of every model directory under ``root``.

    Parameters
    ----------
    root : Path
        Directory holding one subdirectory per evaluated model.
    params : dict[str, float]
        Model parameter counts in millions, keyed by directory name.

    Returns
    -------
    list[ModelRun]
        One entry per model directory, ordered as given in ``params``.

    Raises
    ------
    FileNotFoundError
        If a required artifact is missing for one of the models.
    """
    runs = []
    for name in params:
        model_dir = root / name
        preds = sorted((model_dir / "f1").glob("*-preds.csv.gz"))
        stats = sorted((model_dir / "f1").glob("*_metrics_stats.json"))
        kappa = sorted((model_dir / "kappa").glob("*_matbench_metrics.txt"))
        if not (preds and stats and kappa):
            raise FileNotFoundError(f"Incomplete artifacts for {name} under {model_dir}")
        runs.append(
            ModelRun(
                name=name,
                preds_csv=preds[0],
                stats_json=stats[0],
                kappa_txt=kappa[0],
                params_m=params[name],
            )
        )
    return runs


def read_mean_srme(path: Path) -> float:
    """
    Extract the mean SRME value from a kappa evaluation report.

    Parameters
    ----------
    path : Path
        Text report written by the kappa evaluation stage.

    Returns
    -------
    float
        Mean symmetric relative mean error of the thermal conductivity.

    Raises
    ------
    ValueError
        If the report does not contain a mean SRME line.
    """
    match = re.search(r"mean SRME:\s*([0-9.eE+-]+)", path.read_text())
    if match is None:
        raise ValueError(f"No mean SRME entry in {path}")
    return float(match.group(1))


def hull_distance_errors(preds_csv: Path) -> pd.Series:
    """
    Compute per-structure convex-hull distance errors on the unique-prototype subset.

    Parameters
    ----------
    preds_csv : Path
        Prediction table carrying an ``e_form_per_atom_dp`` column.

    Returns
    -------
    pd.Series
        Signed errors ``each_pred - each_true`` in eV/atom, NaN entries dropped.
    """
    from matbench_discovery.data import df_wbm
    from matbench_discovery.enums import MbdKey

    preds = pd.read_csv(preds_csv).set_index("material_id")
    aligned = df_wbm.copy()
    aligned["model"] = preds["e_form_per_atom_dp"]
    aligned = aligned.round(3)

    unique = aligned[df_wbm["unique_prototype"]]
    each_pred = unique[MbdKey.each_true] + unique["model"] - unique[MbdKey.e_form_dft]
    errors = each_pred - unique[MbdKey.each_true]
    return errors.dropna()


def regression_metrics(errors: pd.Series, each_true: pd.Series) -> dict[str, float]:
    """
    Evaluate MAE, RMSE and R2 from hull-distance errors.

    Parameters
    ----------
    errors : pd.Series
        Signed hull-distance errors in eV/atom.
    each_true : pd.Series
        Reference hull distances in eV/atom, aligned with ``errors``.

    Returns
    -------
    dict[str, float]
        Mapping with keys ``MAE``, ``RMSE`` and ``R2``.
    """
    residual = float((errors**2).sum())
    total = float(((each_true - each_true.mean()) ** 2).sum())
    return {
        "MAE": float(errors.abs().mean()),
        "RMSE": float(np.sqrt((errors**2).mean())),
        "R2": 1.0 - residual / total,
    }


def classification_metrics(errors: pd.Series, each_true: pd.Series) -> dict[str, float]:
    """
    Evaluate stability-classification metrics at the zero-hull-distance threshold.

    Parameters
    ----------
    errors : pd.Series
        Signed hull-distance errors in eV/atom.
    each_true : pd.Series
        Reference hull distances in eV/atom, aligned with ``errors``.

    Returns
    -------
    dict[str, float]
        Mapping with keys ``Accuracy``, ``F1``, ``Precision`` and ``DAF``.
    """
    from matbench_discovery.data import df_wbm
    from matbench_discovery.enums import MbdKey

    each_pred = each_true + errors
    true_pos = each_true <= STABILITY_THRESHOLD
    pred_pos = each_pred <= STABILITY_THRESHOLD

    n_tp = int((true_pos & pred_pos).sum())
    n_fp = int((~true_pos & pred_pos).sum())
    n_fn = int((true_pos & ~pred_pos).sum())
    n_tn = int((~true_pos & ~pred_pos).sum())

    precision = n_tp / (n_tp + n_fp)
    recall = n_tp / (n_tp + n_fn)
    prevalence = float(
        (df_wbm.query("unique_prototype")[MbdKey.each_true] <= STABILITY_THRESHOLD).mean()
    )
    return {
        "Accuracy": (n_tp + n_tn) / len(each_true),
        "F1": 2 * precision * recall / (precision + recall),
        "Precision": precision,
        "DAF": precision / prevalence,
    }


def cps(f1: float, ksrme: float, rmsd: float) -> float:
    """
    Combine F1, kappa SRME and RMSD into the leaderboard combined performance score.

    Parameters
    ----------
    f1 : float
        Stability-classification F1 score.
    ksrme : float
        Symmetric relative mean error of the thermal conductivity.
    rmsd : float
        Mean structural root-mean-square deviation versus DFT, in \\AA.

    Returns
    -------
    float
        Combined performance score on the unit interval.
    """
    return (
        0.5 * np.clip(f1, 0, 1)
        + 0.4 * np.clip(1 - ksrme / 2, 0, 1)
        + 0.1 * np.clip(1 - rmsd / RMSD_BASELINE, 0, 1)
    )


def evaluate(run: ModelRun, error_cutoff: float) -> dict[str, object]:
    """
    Evaluate all leaderboard metrics for one model run.

    Parameters
    ----------
    run : ModelRun
        Artifact paths and parameter count of the evaluated checkpoint.
    error_cutoff : float
        Absolute hull-distance error in eV/atom above which a structure is treated
        as a relaxation failure and excluded from the regression metrics.

    Returns
    -------
    dict[str, object]
        Metric values plus the identifiers and errors of the excluded failures.
    """
    from matbench_discovery.data import df_wbm
    from matbench_discovery.enums import MbdKey

    errors = hull_distance_errors(run.preds_csv)
    each_true = df_wbm.round(3).loc[errors.index, MbdKey.each_true]
    kept = errors.abs() <= error_cutoff

    record: dict[str, object] = {"model": run.name, "params_M": run.params_m}
    record.update(classification_metrics(errors, each_true))
    record.update({f"{k}_all": v for k, v in regression_metrics(errors, each_true).items()})
    record.update(
        {
            f"{k}_trim": v
            for k, v in regression_metrics(errors[kept], each_true[kept]).items()
        }
    )
    record["kSRME"] = read_mean_srme(run.kappa_txt)
    record["RMSD"] = json.loads(run.stats_json.read_text())["rmsd"]
    record["CPS"] = float(cps(record["F1"], record["kSRME"], record["RMSD"]))
    record["failures"] = {mat_id: float(errors[mat_id]) for mat_id in errors.index[~kept]}
    record["n_eval"] = len(errors)
    return record


def main() -> None:
    """Print leaderboard metrics for every model directory found under the root."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.home() / "Downloads/Matbench_Test/Final",
        help="Directory holding one subdirectory per evaluated model.",
    )
    parser.add_argument(
        "--error-cutoff",
        type=float,
        default=5.0,
        help="Hull-distance error in eV/atom above which a structure is excluded "
        "from MAE, RMSE and R2 as a relaxation failure.",
    )
    args = parser.parse_args()

    params = {"Pro": 25.211, "Plus": 8.796, "Air": 5.148, "Neo": 1.125}
    records = [evaluate(run, args.error_cutoff) for run in discover_runs(args.root, params)]

    columns = [
        "model",
        "CPS",
        "Accuracy",
        "F1",
        "DAF",
        "Precision",
        "MAE_all",
        "R2_all",
        "MAE_trim",
        "RMSE_trim",
        "R2_trim",
        "kSRME",
        "RMSD",
        "params_M",
    ]
    table = pd.DataFrame(records)[columns]
    pd.set_option("display.width", 200)
    print(table.to_string(index=False, float_format=lambda v: f"{v:.4f}"))

    print(f"\nRelaxation failures excluded (|error| > {args.error_cutoff} eV/atom):")
    for record in records:
        failures = record["failures"]
        excluded = ", ".join(f"{k}: {v:+.3g}" for k, v in failures.items())
        print(f"  {record['model']:5s} n_eval={record['n_eval']} n_excl={len(failures)}  {excluded}")


if __name__ == "__main__":
    main()

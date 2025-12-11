import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional


# Helpers
def precision_recall_f1(y_true, y_pred, labels: List[str]) -> pd.DataFrame:
    """
    Compute precision, recall, and F1-score for each label.
    Returns a DataFrame where each row corresponds to one label.
    """
    rows = []

    # Loop through each label and compute metrics separately
    for lab in labels:
        # True positives: label correctly predicted
        tp = np.sum((y_true == lab) & (y_pred == lab))

        # False positives: label predicted but not present in ground truth
        fp = np.sum((y_true != lab) & (y_pred == lab))

        # False negatives: label present in ground truth but not predicted
        fn = np.sum((y_true == lab) & (y_pred != lab))

        # Precision: fraction of predicted positives that are correct
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0

        # Recall: fraction of actual positives that are correctly predicted
        rec  = tp / (tp + fn) if (tp + fn) > 0 else 0.0

        # F1: harmonic mean of precision and recall
        f1   = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0

        # Support: number of ground-truth samples for this label
        support = np.sum(y_true == lab)

        rows.append({
            "label": lab,
            "precision": prec,
            "recall": rec,
            "f1": f1,
            "support": support,
            "tp": tp, "fp": fp, "fn": fn
        })

    return pd.DataFrame(rows)


def macro_weighted(df: pd.DataFrame) -> Dict[str, float]:
    """
    Compute macro-averaged and support-weighted precision, recall, and F1.
    Macro: simple average over labels.
    Weighted: average weighted by each label's support.
    """
    # Macro averages: treat each label equally
    macro = {
        "precision_macro": df["precision"].mean(),
        "recall_macro": df["recall"].mean(),
        "f1_macro": df["f1"].mean(),
    }

    # Total number of samples across all labels
    total = df["support"].sum()

    # Weighted averages: labels with more samples have higher influence
    if total == 0:
        weighted = {"precision_weighted": 0.0, "recall_weighted": 0.0, "f1_weighted": 0.0}
    else:
        weighted = {
            "precision_weighted": (df["precision"] * df["support"]).sum() / total,
            "recall_weighted": (df["recall"] * df["support"]).sum() / total,
            "f1_weighted": (df["f1"] * df["support"]).sum() / total,
        }

    # Merge macro and weighted statistics into a single dictionary
    return {**macro, **weighted}


def confusion_matrix(y_true, y_pred, labels: List[str]) -> pd.DataFrame:
    """
    Build a confusion matrix DataFrame where rows are ground-truth labels
    and columns are predicted labels.
    """
    # Initialize empty matrix of counts
    mat = np.zeros((len(labels), len(labels)), dtype=int)

    # Map each label to an index in the matrix
    idx = {lab: i for i, lab in enumerate(labels)}

    # Fill matrix with counts for each (ground-truth, predicted) pair
    for t, p in zip(y_true, y_pred):
        if t in idx and p in idx:
            mat[idx[t], idx[p]] += 1

    return pd.DataFrame(mat, index=labels, columns=labels)


def phase_iou(y_true, y_pred, labels: List[str]) -> pd.DataFrame:
    """
    IoU per class:
      IoU_c = TP_c / (TP_c + FP_c + FN_c)
    """
    rows = []

    # Compute intersection-over-union for each label
    for lab in labels:
        tp = np.sum((y_true == lab) & (y_pred == lab))
        fp = np.sum((y_true != lab) & (y_pred == lab))
        fn = np.sum((y_true == lab) & (y_pred != lab))
        denom = tp + fp + fn

        # IoU is zero when there are no relevant samples
        iou = tp / denom if denom > 0 else 0.0
        rows.append({"label": lab, "iou": iou, "tp": tp, "fp": fp, "fn": fn})

    return pd.DataFrame(rows)


def count_transitions(phases: List[str]) -> List[Tuple[int, str, str]]:
    """Return list of (frame_idx, from_phase, to_phase) transitions."""
    trans = []

    # Compare each phase with the previous phase to detect changes
    for i in range(1, len(phases)):
        if phases[i] != phases[i - 1]:
            trans.append((i, phases[i - 1], phases[i]))

    return trans


def transition_accuracy(gt_phases, pred_phases) -> float:
    """
    Compute transition accuracy:
    fraction of ground-truth transitions that are matched by predicted transitions.
    """
    # Represent transitions as (from_phase, to_phase) pairs, ignoring frame index
    gt_t = set((frm, to) for _, frm, to in count_transitions(gt_phases))
    pr_t = set((frm, to) for _, frm, to in count_transitions(pred_phases))

    # If there are no ground-truth transitions, accuracy is zero
    if len(gt_t) == 0:
        return 0.0

    # Correct transitions are those present in both sets
    correct = len(gt_t.intersection(pr_t))
    return correct / len(gt_t)


# ---------------------------
# Main metrics
# ---------------------------

def compute_metrics(
    pred_frame_csv: str,
    gt_frame_csv: str,
    pred_rep_csv: Optional[str] = None,
    gt_total_reps: Optional[int] = None,
    save_dir: str = "reports/metrics"
):
    """
    Compute a collection of metrics for phase predictions and, optionally, rep counts.
    Results are saved as CSV files in the target directory and returned as a dictionary.
    """
    # Create output directory if it does not exist
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    # Load predicted frame-level log and ground-truth frame-level log
    pred = pd.read_csv(pred_frame_csv)
    gt = pd.read_csv(gt_frame_csv)

    # Align predicted and ground-truth data by frame index
    merged = pd.merge(pred, gt, on="frame_idx", how="inner")
    if merged.empty:
        raise ValueError("No overlapping frame_idx between pred and ground truth.")

    # Extract phase sequences from merged DataFrame
    y_true = merged["phase_gt"].astype(str).values
    y_pred = merged["phase"].astype(str).values

    # Collect all labels appearing in either ground-truth or predictions
    labels = sorted(list(set(y_true) | set(y_pred)))

    # ---- Phase frame-wise accuracy ----
    # Simple fraction of frames where the phase prediction matches ground truth
    frame_acc = float(np.mean(y_true == y_pred))

    # ---- Precision / Recall / F1 ----
    prf_df = precision_recall_f1(y_true, y_pred, labels)
    prf_summary = macro_weighted(prf_df)

    # ---- IoU ----
    iou_df = phase_iou(y_true, y_pred, labels)
    mean_iou = float(iou_df["iou"].mean())

    # ---- Confusion matrix ----
    cm_df = confusion_matrix(y_true, y_pred, labels)

    # ---- Transition accuracy ----
    trans_acc = float(transition_accuracy(list(y_true), list(y_pred)))

    # ---- Exercise classifier accuracy (if ground truth includes exercise_gt) ----
    ex_acc = None
    if "exercise_gt" in merged.columns and "exercise" in merged.columns:
        ex_acc = float(np.mean(
            merged["exercise_gt"].astype(str).values ==
            merged["exercise"].astype(str).values
        ))

    # ---- Rep metrics (optional) ----
    rep_metrics = {}
    if pred_rep_csv and gt_total_reps is not None:
        # Load predicted rep-level log
        pred_rep = pd.read_csv(pred_rep_csv)

        # Predicted rep count is the maximum rep_id present
        r_pred = int(pred_rep["rep_id"].max()) if len(pred_rep) else 0

        # Ground-truth total rep count is provided as an argument
        r_gt = int(gt_total_reps)

        # Absolute error between predicted and ground-truth rep counts
        ae = abs(r_pred - r_gt)

        # Rep accuracy: scaled measure of count agreement
        acc_rep = 1 - (ae / r_gt) if r_gt > 0 else 0.0

        rep_metrics = {
            "rep_pred": r_pred,
            "rep_gt": r_gt,
            "rep_abs_error": ae,
            "rep_accuracy": float(acc_rep)
        }

    # ---- Pack results into a single dictionary ----
    results = {
        "frame_accuracy": frame_acc,
        "transition_accuracy": trans_acc,
        "mean_iou": mean_iou,
        **prf_summary,
        **rep_metrics
    }
    if ex_acc is not None:
        results["exercise_accuracy"] = ex_acc

    # ---- Save outputs to CSV files ----
    pd.DataFrame([results]).to_csv(save_dir / "summary_metrics.csv", index=False)
    prf_df.to_csv(save_dir / "per_phase_prf.csv", index=False)
    iou_df.to_csv(save_dir / "per_phase_iou.csv", index=False)
    cm_df.to_csv(save_dir / "confusion_matrix.csv")

    # Print summary to console for quick inspection
    print("\n=== Summary Metrics ===")
    for k, v in results.items():
        print(f"{k:22s}: {v:.4f}" if isinstance(v, float) else f"{k:22s}: {v}")

    print("\nSaved:")
    print(" -", save_dir / "summary_metrics.csv")
    print(" -", save_dir / "per_phase_prf.csv")
    print(" -", save_dir / "per_phase_iou.csv")
    print(" -", save_dir / "confusion_matrix.csv")

    return results


if __name__ == "__main__":
    import argparse

    # Command-line interface for running metric computation directly
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred_frames", default="reports/frame_log.csv")
    ap.add_argument("--gt_frames", required=True)
    ap.add_argument("--pred_reps", default=None)
    ap.add_argument("--gt_reps", type=int, default=None)
    ap.add_argument("--save_dir", default="reports/metrics")
    args = ap.parse_args()

    # Run metrics computation with provided paths and settings
    compute_metrics(
        pred_frame_csv=args.pred_frames,
        gt_frame_csv=args.gt_frames,
        pred_rep_csv=args.pred_reps,
        gt_total_reps=args.gt_reps,
        save_dir=args.save_dir
    )

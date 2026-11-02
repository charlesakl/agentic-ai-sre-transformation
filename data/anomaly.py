"""Reproducible, synthetic P95 exception-volume anomaly detector."""
import numpy as np
import pandas as pd


def synthetic_history(service: str, days: int = 90, seed: int = 42) -> pd.DataFrame:
    """10-minute exception counts, including normal daily variation."""
    rng = np.random.default_rng(seed + sum(map(ord, service)))
    periods = days * 24 * 6
    timestamps = pd.date_range('2026-08-01', periods=periods, freq='10min')
    hour = timestamps.hour.to_numpy()
    weekday = timestamps.dayofweek.to_numpy()
    traffic_factor = np.where((hour >= 8) & (hour < 19), 1.4, 0.7)
    traffic_factor *= np.where(weekday < 5, 1.15, 0.85)
    counts = rng.poisson(10 * traffic_factor)
    return pd.DataFrame({'time': timestamps, 'exceptions': counts})


def detect_p95(history: pd.DataFrame, current_count: int) -> dict:
    threshold = float(np.percentile(history['exceptions'].to_numpy(), 95))
    return {'threshold': threshold, 'current': int(current_count),
            'is_anomaly': bool(current_count > threshold),
            'ratio': float(current_count / threshold) if threshold else None,
            'history_intervals': len(history)}

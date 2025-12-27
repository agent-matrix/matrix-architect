"""Metrics collection for Prometheus"""

import time
from typing import Dict, Any
from collections import defaultdict
from threading import Lock


class MetricsCollector:
    """Simple metrics collector (production would use prometheus_client)"""

    def __init__(self):
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, list] = defaultdict(list)
        self._lock = Lock()

    def inc_counter(self, name: str, value: int = 1, labels: Dict[str, str] = None):
        """Increment a counter"""
        key = self._make_key(name, labels)
        with self._lock:
            self._counters[key] += value

    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Set a gauge value"""
        key = self._make_key(name, labels)
        with self._lock:
            self._gauges[key] = value

    def observe_histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """Record a histogram observation"""
        key = self._make_key(name, labels)
        with self._lock:
            self._histograms[key].append(value)

    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics"""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    k: {
                        "count": len(v),
                        "sum": sum(v),
                        "avg": sum(v) / len(v) if v else 0,
                        "min": min(v) if v else 0,
                        "max": max(v) if v else 0,
                    }
                    for k, v in self._histograms.items()
                }
            }

    def _make_key(self, name: str, labels: Dict[str, str] = None) -> str:
        """Make a metric key from name and labels"""
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"


# Global metrics instance
_metrics = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector"""
    return _metrics


# Decorator for timing functions
def time_function(metric_name: str):
    """Decorator to time function execution"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start
                _metrics.observe_histogram(metric_name, duration)
        return wrapper
    return decorator

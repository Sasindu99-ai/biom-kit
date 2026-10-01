"""
Premade tools suite for BIOM datasets:
- cleaning: missing values, types, outliers, health audit
- analysis: summary statistics, correlations, cohort aggregations, comparisons
- plotting: publication-ready distributions, heatmaps, box plots, time series
"""

from .analysis import (
	compare_groups,
	correlation_matrix,
	group_summary,
	summarize,
)
from .cleaning import (
	clean_dataset,
	detect_outliers,
	impute_missing,
	summarize_health,
)
from .plotting import (
	plot_comparison,
	plot_correlation_matrix,
	plot_distribution,
	plot_missingness,
	plot_time_series,
)

__all__ = [
	'clean_dataset',
	'compare_groups',
	'correlation_matrix',
	'detect_outliers',
	'group_summary',
	'impute_missing',
	'plot_comparison',
	'plot_correlation_matrix',
	'plot_distribution',
	'plot_missingness',
	'plot_time_series',
	'summarize',
	'summarize_health',
]

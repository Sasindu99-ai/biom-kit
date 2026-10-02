"""
Premade statistical analysis and cohort comparison utilities for BIOM datasets.
"""

from typing import Any

import numpy as np
import pandas as pd

__all__ = [
	'compare_groups',
	'correlation_matrix',
	'group_summary',
	'summarize',
]


def summarize(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
	"""
	Produces extended descriptive statistics for numeric biomarkers and variables:
	count, missing, mean, std, min, 25%, median, 75%, max, IQR, skewness.
	"""
	numeric_df = df[columns] if columns else df.select_dtypes(include=[np.number])
	if numeric_df.empty:
		return pd.DataFrame()

	records = []
	for col in numeric_df.columns:
		series = pd.to_numeric(numeric_df[col], errors='coerce').dropna()
		if len(series) == 0:
			continue

		q25 = float(series.quantile(0.25))
		q75 = float(series.quantile(0.75))
		records.append({
			'variable': col,
			'count': len(series),
			'missing': int(df[col].isna().sum()),
			'mean': round(float(series.mean()), 3),
			'std': round(float(series.std()), 3),
			'min': round(float(series.min()), 3),
			'25%': round(q25, 3),
			'median': round(float(series.median()), 3),
			'75%': round(q75, 3),
			'max': round(float(series.max()), 3),
			'iqr': round(q75 - q25, 3),
			'skewness': round(float(series.skew()), 3) if len(series) > 2 else np.nan,
		})

	return pd.DataFrame(records).reset_index(drop=True)


def correlation_matrix(
	df: pd.DataFrame,
	columns: list[str] | None = None,
	method: str = 'pearson',
) -> pd.DataFrame:
	"""
	Computes correlation matrix between numeric variables.
	"""
	numeric_df = df[columns] if columns else df.select_dtypes(include=[np.number])
	if numeric_df.empty:
		return pd.DataFrame()

	corr = numeric_df.corr(method=method)
	return corr.round(3)


def group_summary(
	df: pd.DataFrame,
	group_by: str,
	target_cols: list[str] | None = None,
	metrics: list[str] | None = None,
) -> pd.DataFrame:
	"""
	Generates aggregated statistics across demographic cohorts or status groups.
	"""
	if group_by not in df.columns:
		raise ValueError(f'Grouping column "{group_by}" not found in DataFrame.')

	target_metrics = metrics or ['count', 'mean', 'median', 'std']
	numeric_cols = target_cols or [c for c in df.select_dtypes(include=[np.number]).columns if c != group_by]

	if not numeric_cols:
		return pd.DataFrame()

	grouped = df.groupby(group_by)[numeric_cols].agg(target_metrics)
	return grouped.round(3)


def compare_groups(df: pd.DataFrame, group_col: str, value_col: str) -> dict[str, Any]:
	"""
	Compares a continuous biomarker across 2 groups (e.g. Male vs Female).
	Calculates group statistics and significance tests.
	"""
	clean = df[[group_col, value_col]].dropna()
	groups = clean[group_col].unique()

	if len(groups) != 2:
		return {
			'error': f'Comparison requires exactly 2 distinct groups, found {len(groups)}: {list(groups)}',
		}

	g1_val = clean[clean[group_col] == groups[0]][value_col]
	g2_val = clean[clean[group_col] == groups[1]][value_col]

	result = {
		'variable': value_col,
		'group_by': group_col,
		'groups': {
			str(groups[0]): {
				'n': len(g1_val),
				'mean': round(float(g1_val.mean()), 3),
				'median': round(float(g1_val.median()), 3),
				'std': round(float(g1_val.std()), 3),
			},
			str(groups[1]): {
				'n': len(g2_val),
				'mean': round(float(g2_val.mean()), 3),
				'median': round(float(g2_val.median()), 3),
				'std': round(float(g2_val.std()), 3),
			},
		},
		'mean_difference': round(float(g1_val.mean() - g2_val.mean()), 3),
	}

	# Try calculating t-test if scipy is installed
	try:
		from scipy import stats
		t_stat, p_val = stats.ttest_ind(g1_val, g2_val, equal_var=False)
		result['t_statistic'] = round(float(t_stat), 3)
		result['p_value'] = float(f'{p_val:.4e}')
		result['significant_p05'] = bool(p_val < 0.05)
	except ImportError:
		result['statistical_test'] = 'Install scipy for automated p-value calculation.'

	return result

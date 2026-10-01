"""
Premade data cleaning utilities for BIOM datasets.
"""

from typing import Any
import numpy as np
import pandas as pd

__all__ = [
	'clean_dataset',
	'detect_outliers',
	'impute_missing',
	'summarize_health',
]


def clean_dataset(
	df: pd.DataFrame,
	drop_empty_cols: bool = True,
	drop_empty_rows: bool = False,
	coerce_numeric: bool = True,
	parse_dates: bool = True,
	trim_strings: bool = True,
) -> pd.DataFrame:
	"""
	Cleans a raw BIOM dataset DataFrame:
	- Coerces numerical strings to numeric dtypes.
	- Parses date columns to pandas datetime.
	- Trims surrounding whitespace from text fields.
	- Standardizes boolean values.
	- Optionally removes completely empty columns or rows.
	"""
	cleaned = df.copy()

	if drop_empty_rows:
		cleaned = cleaned.dropna(how='all')

	if drop_empty_cols:
		cleaned = cleaned.dropna(axis=1, how='all')

	for col in cleaned.columns:
		# Trim strings
		if trim_strings and (cleaned[col].dtype == object or pd.api.types.is_string_dtype(cleaned[col])):
			try:
				cleaned[col] = cleaned[col].str.strip()
			except (AttributeError, TypeError):
				cleaned[col] = cleaned[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

		# Parse dates
		if parse_dates and any(term in col.lower() for term in ['date', 'dob', 'created_at', 'tested']):
			try:
				parsed = pd.to_datetime(cleaned[col], errors='coerce')
				# If at least half the non-null values parsed successfully, convert
				if parsed.notna().sum() >= max(cleaned[col].notna().sum() * 0.5, 1):
					cleaned[col] = parsed
			except Exception:
				pass

		# Coerce numeric values (biomarkers, age, etc.)
		is_str_or_obj = cleaned[col].dtype == object or pd.api.types.is_string_dtype(cleaned[col]) or pd.api.types.is_object_dtype(cleaned[col])
		if coerce_numeric and is_str_or_obj:
			try:
				numeric = pd.to_numeric(cleaned[col], errors='coerce')
				# If more than 70% of non-null values are numeric, convert to numeric
				non_null_count = cleaned[col].notna().sum()
				if non_null_count > 0 and (numeric.notna().sum() / non_null_count) >= 0.7:
					cleaned[col] = numeric
			except Exception:
				pass

	return cleaned


def summarize_health(df: pd.DataFrame) -> pd.DataFrame:
	"""
	Generates a data health audit report including missingness, unique counts, and dtypes.
	"""
	records = []
	total_rows = len(df)

	for col in df.columns:
		missing_count = df[col].isna().sum()
		missing_pct = (missing_count / total_rows * 100) if total_rows > 0 else 0
		unique_count = df[col].nunique(dropna=True)
		dtype = str(df[col].dtype)

		records.append({
			'column': col,
			'dtype': dtype,
			'non_null_count': total_rows - missing_count,
			'missing_count': missing_count,
			'missing_pct': round(missing_pct, 2),
			'unique_values': unique_count,
		})

	return pd.DataFrame(records).sort_values(by='missing_pct', ascending=False).reset_index(drop=True)


def detect_outliers(
	df: pd.DataFrame,
	columns: list[str] | None = None,
	method: str = 'iqr',
	threshold: float = 1.5,
) -> pd.DataFrame:
	"""
	Detects statistical outliers in numeric columns using IQR (Interquartile Range).
	Returns a boolean DataFrame where True indicates an outlier.
	"""
	target_cols = columns or df.select_dtypes(include=[np.number]).columns.tolist()
	outlier_mask = pd.DataFrame(False, index=df.index, columns=target_cols)

	for col in target_cols:
		series = pd.to_numeric(df[col], errors='coerce')
		if series.notna().sum() < 4:
			continue

		if method.lower() == 'iqr':
			q1 = series.quantile(0.25)
			q3 = series.quantile(0.75)
			iqr = q3 - q1
			lower_bound = q1 - threshold * iqr
			upper_bound = q3 + threshold * iqr
			outlier_mask[col] = (series < lower_bound) | (series > upper_bound)
		elif method.lower() == 'zscore':
			mean = series.mean()
			std = series.std()
			if std > 0:
				z = (series - mean).abs() / std
				outlier_mask[col] = z > threshold

	return outlier_mask


def impute_missing(
	df: pd.DataFrame,
	columns: list[str] | None = None,
	strategy: str = 'median',
) -> pd.DataFrame:
	"""
	Imputes missing values:
	- Numeric columns: 'median' or 'mean'
	- Categorical columns: 'mode' or 'unknown'
	"""
	imputed = df.copy()
	target_cols = columns or df.columns.tolist()

	for col in target_cols:
		if imputed[col].isna().sum() == 0:
			continue

		if pd.api.types.is_numeric_dtype(imputed[col]):
			if strategy == 'mean':
				fill_val = imputed[col].mean()
			else:
				fill_val = imputed[col].median()
			imputed[col] = imputed[col].fillna(fill_val)
		else:
			mode_val = imputed[col].mode()
			fill_val = mode_val.iloc[0] if not mode_val.empty else 'Unknown'
			imputed[col] = imputed[col].fillna(fill_val)

	return imputed

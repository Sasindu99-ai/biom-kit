import numpy as np
import pandas as pd
from biom.tools.cleaning import (
	clean_dataset,
	detect_outliers,
	impute_missing,
	summarize_health,
)


def test_clean_dataset(sample_raw_df):
	cleaned = clean_dataset(sample_raw_df)

	# Verify AllEmpty column was dropped
	assert 'AllEmpty' not in cleaned.columns

	# Verify whitespace in references was trimmed
	assert cleaned['reference'].iloc[0] == 'PAT-001'
	assert cleaned['reference'].iloc[2] == 'PAT-003'

	# Verify numeric coercion
	assert pd.api.types.is_numeric_dtype(cleaned['age'])
	assert pd.api.types.is_numeric_dtype(cleaned['Glucose'])
	assert pd.api.types.is_numeric_dtype(cleaned['SystolicBP'])
	assert cleaned['Glucose'].iloc[0] == 95.5

	# Verify date parsing
	assert pd.api.types.is_datetime64_any_dtype(cleaned['testedDate'])


def test_summarize_health(sample_raw_df):
	report = summarize_health(sample_raw_df)

	assert isinstance(report, pd.DataFrame)
	assert 'column' in report.columns
	assert 'missing_pct' in report.columns
	assert 'unique_values' in report.columns

	all_empty_row = report[report['column'] == 'AllEmpty']
	assert len(all_empty_row) == 1
	assert all_empty_row['missing_pct'].iloc[0] == 100.0


def test_detect_outliers():
	df = pd.DataFrame({
		'Glucose': [90, 92, 95, 96, 98, 100, 102, 105, 500],  # 500 is extreme outlier
	})
	outliers = detect_outliers(df, method='iqr', threshold=1.5)

	assert isinstance(outliers, pd.DataFrame)
	assert 'Glucose' in outliers.columns
	assert not outliers['Glucose'].iloc[0]
	assert outliers['Glucose'].iloc[-1]  # 500 is flagged as True


def test_impute_missing():
	df = pd.DataFrame({
		'Glucose': [100.0, 110.0, np.nan, 120.0],
		'Gender': ['Female', 'Female', np.nan, 'Male'],
	})
	imputed = impute_missing(df, strategy='median')

	# Median of [100, 110, 120] is 110
	assert imputed['Glucose'].isna().sum() == 0
	assert imputed['Glucose'].iloc[2] == 110.0

	# Mode of ['Female', 'Female', 'Male'] is 'Female'
	assert imputed['Gender'].isna().sum() == 0
	assert imputed['Gender'].iloc[2] == 'Female'

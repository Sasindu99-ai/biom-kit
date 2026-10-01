import pandas as pd

from biom.tools.analysis import (
	compare_groups,
	correlation_matrix,
	group_summary,
	summarize,
)


def test_summarize(sample_numeric_df):
	summary = summarize(sample_numeric_df)

	assert isinstance(summary, pd.DataFrame)
	assert 'variable' in summary.columns
	assert 'mean' in summary.columns
	assert 'median' in summary.columns
	assert 'iqr' in summary.columns

	glucose_row = summary[summary['variable'] == 'Glucose']
	assert len(glucose_row) == 1
	assert glucose_row['count'].iloc[0] == 8


def test_correlation_matrix(sample_numeric_df):
	corr = correlation_matrix(sample_numeric_df)

	assert isinstance(corr, pd.DataFrame)
	assert 'Glucose' in corr.columns
	assert 'Cholesterol' in corr.columns
	# Diagonal is 1.0
	assert corr.loc['Glucose', 'Glucose'] == 1.0
	assert corr.loc['Cholesterol', 'Cholesterol'] == 1.0
	# Positive correlation between age and Glucose in sample data
	assert corr.loc['age', 'Glucose'] > 0


def test_group_summary(sample_numeric_df):
	grouped = group_summary(sample_numeric_df, group_by='gender', target_cols=['Glucose'])

	assert isinstance(grouped, pd.DataFrame)
	assert len(grouped) == 2  # F and M


def test_compare_groups(sample_numeric_df):
	res = compare_groups(sample_numeric_df, group_col='gender', value_col='Glucose')

	assert isinstance(res, dict)
	assert res['variable'] == 'Glucose'
	assert res['group_by'] == 'gender'
	assert 'groups' in res
	assert 'F' in res['groups']
	assert 'M' in res['groups']
	assert 'mean_difference' in res

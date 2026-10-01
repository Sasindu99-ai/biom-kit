import matplotlib.pyplot as plt
import pandas as pd

from biom.tools.plotting import (
	plot_comparison,
	plot_correlation_matrix,
	plot_distribution,
	plot_missingness,
	plot_time_series,
)


def test_plot_distribution(sample_numeric_df):
	fig = plot_distribution(sample_numeric_df, column='Glucose', hue='gender')
	assert isinstance(fig, plt.Figure)
	plt.close(fig)


def test_plot_correlation_matrix(sample_numeric_df):
	fig = plot_correlation_matrix(sample_numeric_df)
	assert isinstance(fig, plt.Figure)
	plt.close(fig)


def test_plot_comparison_box(sample_numeric_df):
	fig = plot_comparison(sample_numeric_df, category_col='gender', value_col='Glucose', kind='box')
	assert isinstance(fig, plt.Figure)
	plt.close(fig)


def test_plot_comparison_violin(sample_numeric_df):
	fig = plot_comparison(sample_numeric_df, category_col='gender', value_col='Glucose', kind='violin')
	assert isinstance(fig, plt.Figure)
	plt.close(fig)


def test_plot_missingness(sample_raw_df):
	fig = plot_missingness(sample_raw_df)
	assert isinstance(fig, plt.Figure)
	plt.close(fig)


def test_plot_time_series(sample_numeric_df):
	fig = plot_time_series(sample_numeric_df, date_col='testedDate', value_col='Glucose', group_by='gender')
	assert isinstance(fig, plt.Figure)
	plt.close(fig)

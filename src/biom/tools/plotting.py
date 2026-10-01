"""
Premade publication-quality visualization tools for BIOM datasets.
Built with clean styling, suitable for Jupyter Notebooks and Google Colab.
"""

from typing import Any
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

__all__ = [
	'plot_comparison',
	'plot_correlation_matrix',
	'plot_distribution',
	'plot_missingness',
	'plot_time_series',
]

# Set default clean aesthetic theme
sns.set_theme(style='whitegrid', palette='muted')


def plot_distribution(
	df: pd.DataFrame,
	column: str,
	hue: str | None = None,
	kde: bool = True,
	bins: int = 30,
	title: str | None = None,
	figsize: tuple[int, int] = (8, 5),
) -> plt.Figure:
	"""
	Plots a distribution histogram with optional KDE and cohort grouping.
	"""
	fig, ax = plt.subplots(figsize=figsize)

	data = df.dropna(subset=[column])
	sns.histplot(
		data=data,
		x=column,
		hue=hue,
		kde=kde,
		bins=bins,
		ax=ax,
		alpha=0.6,
	)

	plot_title = title or f'Distribution of {column}' + (f' by {hue}' if hue else '')
	ax.set_title(plot_title, fontsize=13, fontweight='bold', pad=12)
	ax.set_xlabel(column, fontsize=11)
	ax.set_ylabel('Count', fontsize=11)
	fig.tight_layout()
	return fig


def plot_correlation_matrix(
	df: pd.DataFrame,
	columns: list[str] | None = None,
	annot: bool = True,
	cmap: str = 'coolwarm',
	figsize: tuple[int, int] = (9, 7),
) -> plt.Figure:
	"""
	Plots a correlation heatmap for numeric biomarkers and demographic fields.
	"""
	numeric_df = df[columns] if columns else df.select_dtypes(include=[np.number])
	corr = numeric_df.corr()

	fig, ax = plt.subplots(figsize=figsize)
	mask = np.triu(np.ones_like(corr, dtype=bool))

	sns.heatmap(
		corr,
		mask=mask,
		annot=annot,
		fmt='.2f',
		cmap=cmap,
		vmin=-1,
		vmax=1,
		square=True,
		linewidths=0.5,
		ax=ax,
		cbar_kws={'shrink': 0.8},
	)

	ax.set_title('Biomarker Correlation Matrix', fontsize=14, fontweight='bold', pad=15)
	fig.tight_layout()
	return fig


def plot_comparison(
	df: pd.DataFrame,
	category_col: str,
	value_col: str,
	kind: str = 'box',
	title: str | None = None,
	figsize: tuple[int, int] = (8, 5),
) -> plt.Figure:
	"""
	Plots a comparison of a continuous biomarker across discrete categories.
	Supports kind='box' or kind='violin'.
	"""
	fig, ax = plt.subplots(figsize=figsize)
	data = df.dropna(subset=[category_col, value_col])

	if kind == 'violin':
		sns.violinplot(data=data, x=category_col, y=value_col, hue=category_col, legend=False, ax=ax, inner='quartile', palette='Set2')
	else:
		sns.boxplot(data=data, x=category_col, y=value_col, hue=category_col, legend=False, ax=ax, palette='Set2', boxprops=dict(alpha=0.8))
		sns.stripplot(data=data, x=category_col, y=value_col, ax=ax, color='black', alpha=0.3, jitter=0.2, size=4)

	plot_title = title or f'{value_col} by {category_col}'
	ax.set_title(plot_title, fontsize=13, fontweight='bold', pad=12)
	ax.set_xlabel(category_col, fontsize=11)
	ax.set_ylabel(value_col, fontsize=11)
	fig.tight_layout()
	return fig


def plot_missingness(df: pd.DataFrame, figsize: tuple[int, int] = (9, 4)) -> plt.Figure:
	"""
	Plots missing data percentages across all columns.
	"""
	total = len(df)
	missing = (df.isna().sum() / total * 100).sort_values(ascending=False)
	missing = missing[missing > 0]

	fig, ax = plt.subplots(figsize=figsize)
	if missing.empty:
		ax.text(0.5, 0.5, 'No missing values found!', ha='center', va='center', fontsize=14, color='green')
		ax.set_axis_off()
		return fig

	sns.barplot(x=missing.values, y=missing.index, hue=missing.index, legend=False, ax=ax, palette='Reds_r')
	ax.set_title('Missing Data Percentage (%)', fontsize=13, fontweight='bold', pad=12)
	ax.set_xlabel('Missing (%)', fontsize=11)
	ax.set_xlim(0, 100)
	fig.tight_layout()
	return fig


def plot_time_series(
	df: pd.DataFrame,
	date_col: str,
	value_col: str,
	group_by: str | None = None,
	figsize: tuple[int, int] = (10, 5),
) -> plt.Figure:
	"""
	Plots a longitudinal trend of biomarker values over time.
	"""
	fig, ax = plt.subplots(figsize=figsize)
	data = df.dropna(subset=[date_col, value_col]).copy()
	data[date_col] = pd.to_datetime(data[date_col], errors='coerce')
	data = data.sort_values(by=date_col)

	sns.lineplot(
		data=data,
		x=date_col,
		y=value_col,
		hue=group_by,
		marker='o',
		ax=ax,
	)

	ax.set_title(f'{value_col} over Time', fontsize=13, fontweight='bold', pad=12)
	ax.set_xlabel('Date', fontsize=11)
	ax.set_ylabel(value_col, fontsize=11)
	fig.autofmt_xdate()
	fig.tight_layout()
	return fig

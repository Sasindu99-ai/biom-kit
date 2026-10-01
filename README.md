# BIOM Kit (`biom-kit`)

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**`biom-kit`** is the official Python client and data science toolkit for the **BIOM** platform. Designed specifically for **Google Colab**, **Jupyter Notebooks**, and Python research pipelines, it makes finding, filtering, analyzing, and plotting clinical study datasets intuitive, robust, and fast.

---

## Key Features

- **Intuitive Discovery**: Discover patient profile fields, available datasets, and biomarker variables directly on command. No memorizing internal column names or IDs.
- **Type-Aware Filtering**: Filter with native Python syntax (`>=`, `==`, `between`, `contains`, etc.) across numbers, dates, categories, and booleans.
- **Fluent & Declarative APIs**: Choose between method-chaining (`ds.filter(...).to_dataframe()`) or declarative `F` expressions.
- **Direct Pandas Integration**: Query results instantly convert into clean `pandas.DataFrame` tables.
- **Premade Data Science Tools**:
  - 🧹 **Cleaning**: Type coercion, missingness imputation, outlier detection, data health audits.
  - 📊 **Analysis**: Multi-cohort statistical summaries, correlation matrices, subgroup comparisons.
  - 📈 **Plotting**: Publication-ready distributions, correlation heatmaps, box/violin cohort comparisons, and time series plots.
- **Secure Authentication**: Authenticate using your personal API key generated from the BIOM web dashboard settings.

---

## Installation

Install using `pip`:

```bash
pip install biom-kit
```

Or install directly in a **Google Colab** cell or virtual environment:

```bash
!pip install git+https://github.com/Sasindu99-ai/BIOM.git#subdirectory=biom-kit
```

---

## Quickstart

### 1. Authentication
Generate your personal API key from the BIOM website under **Dashboard > Settings & API Keys** (`/dashboard/settings`).

```python
import biom

# Authenticate with your personal API key (automatically targets https://biom.arceion.com)
biom.login(api_key="biom_live_a1b2c3d4...")

# Or explicitly set a custom/local base URL:
# biom.login(api_key="biom_live_a1b2c3d4...", base_url="https://biom.arceion.com")
```

---

### 2. Discover Fields, Datasets & Variables

When working in Jupyter or Colab, discovery commands automatically render interactive, rich HTML tables:

```python
# 1. Discover all filterable patient profile fields & valid operators
biom.fields()

# 2. List available clinical datasets
biom.datasets()

# 3. Inspect all variables in a specific dataset (by ID or name)
biom.variables(1)

# 4. Search variables across all studies
biom.search_variables("glucose")
```

---

### 3. Filter & Retrieve Data

#### Style A: Fluent Method Chaining (Recommended)

```python
# Select dataset and chain filters
df = (
    biom.dataset(1)
    .filter(age__gte=18, age__lte=65)
    .filter(gender="Female")
    .filter("Glucose", gt=100)
    .filter(testedDate__between=("2024-01-01", "2024-12-31"))
    .sort_by("age", ascending=True)
    .to_dataframe()
)

print(df.head())
```

#### Style B: Declarative `F` Expressions

```python
from biom import F

df = biom.query(
    dataset=1,
    filters=[
        F("age") >= 18,
        F("gender") == "Female",
        F("Glucose") > 100,
        F("testedDate").between("2024-01-01", "2024-12-31"),
    ],
).to_dataframe()
```

#### Style C: Multi-Dataset Combined Query

```python
# Query across multiple datasets simultaneously:
df = biom.query(
    datasets=[1, 2],
    filters=[
        F("age") >= 40,
        F("Smoker") == True,
    ],
).to_dataframe()
```

---

## 4. Premade Tools Suite (`biom.tools`)

### 🧹 Data Cleaning

```python
# 1. Comprehensive dataset cleaning (coerces numbers, parses dates, trims whitespace)
clean_df = biom.tools.clean_dataset(df)

# 2. Data Health & Missingness Audit
health_report = biom.tools.summarize_health(clean_df)
print(health_report)

# 3. Detect Statistical Outliers (IQR or Z-Score)
outliers = biom.tools.detect_outliers(clean_df, columns=["Glucose"], method="iqr")

# 4. Impute Missing Values
imputed_df = biom.tools.impute_missing(clean_df, strategy="median")
```

---

### 📊 Statistical Analysis

```python
# 1. Extended summary statistics (mean, median, IQR, skewness, min, max)
stats = biom.tools.summarize(clean_df)

# 2. Correlation matrix across biomarkers and demographic fields
corr = biom.tools.correlation_matrix(clean_df)

# 3. Cohort Group Aggregation
summary_by_gender = biom.tools.group_summary(clean_df, group_by="gender")

# 4. Two-Sample Cohort Comparison & Significance
diff = biom.tools.compare_groups(clean_df, group_col="gender", value_col="Glucose")
print(diff)
```

---

### 📈 Publication-Quality Plotting

```python
# 1. Distribution histogram with KDE and cohort hue
fig = biom.tools.plot_distribution(clean_df, column="Glucose", hue="gender")

# 2. Correlation heatmap
fig = biom.tools.plot_correlation_matrix(clean_df)

# 3. Box plot / Violin comparison with jitter points
fig = biom.tools.plot_comparison(clean_df, category_col="gender", value_col="Glucose", kind="box")

# 4. Missing data visualization
fig = biom.tools.plot_missingness(clean_df)

# 5. Longitudinal time series trend
fig = biom.tools.plot_time_series(clean_df, date_col="testedDate", value_col="Glucose", group_by="gender")
```

---

## Filter Operator Reference

| Data Type | Supported Operators | Example Syntax |
|---|---|---|
| **Number** | `equals`, `gt`, `gte`, `lt`, `lte`, `between`, `is_empty`, `is_not_empty` | `age__gte=18`, `F("Glucose") > 110`, `age__between=(20, 60)` |
| **Date** | `equals`, `before`, `after`, `between`, `is_empty`, `is_not_empty` | `testedDate__after="2024-01-01"`, `F("dateOfBirth").before("2000-01-01")` |
| **Text** | `equals`, `contains`, `starts_with`, `ends_with`, `is_empty`, `is_not_empty` | `gender="Female"`, `reference__startswith="CV-"`, `F("notes").contains("hypertension")` |
| **Boolean** | `equals`, `is_empty`, `is_not_empty` | `Smoker=True`, `F("Hypertension") == True` |

---

## License
MIT License.

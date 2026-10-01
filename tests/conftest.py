"""
Pytest configuration and shared fixtures for biom-kit tests.
"""

import matplotlib
import pandas as pd
import pytest

# Use non-interactive backend for headless CI/testing
matplotlib.use('Agg')


@pytest.fixture
def sample_raw_df():
	"""Returns a representative raw BIOM DataFrame before cleaning."""
	return pd.DataFrame({
		'patientId': [101, 102, 103, 104, 105],
		'reference': [' PAT-001 ', 'PAT-002', 'PAT-003 ', 'PAT-004', 'PAT-005'],
		'age': ['25', '45', '65', '35', '70'],
		'gender': ['Female', 'Male', 'Female', 'Male', 'Female'],
		'testedDate': ['2024-01-15', '2024-02-20', '2024-03-10', '2024-04-05', '2024-05-12'],
		'Glucose': ['95.5', '115.0', '180.2', '102.0', '110.5'],
		'SystolicBP': ['120', '135', '160', '118', '125'],
		'Smoker': ['False', 'True', 'False', 'False', 'True'],
		'AllEmpty': [None, None, None, None, None],
	})


@pytest.fixture
def sample_numeric_df():
	"""Returns a clean numeric DataFrame for testing statistical and plotting tools."""
	return pd.DataFrame({
		'age': [25.0, 30.0, 45.0, 50.0, 60.0, 65.0, 70.0, 75.0],
		'gender': ['F', 'F', 'M', 'M', 'F', 'F', 'M', 'M'],
		'Glucose': [90.0, 95.0, 110.0, 115.0, 130.0, 135.0, 170.0, 180.0],
		'Cholesterol': [180.0, 190.0, 210.0, 220.0, 230.0, 240.0, 260.0, 280.0],
		'testedDate': pd.date_range('2024-01-01', periods=8, freq='15D'),
	})

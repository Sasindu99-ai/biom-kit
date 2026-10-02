from unittest.mock import MagicMock, patch

import pandas as pd
from biom import BiomClient
from biom.models import DatasetCatalog, FieldCatalog, VariableCatalog


def test_fields_discovery():
	client = BiomClient(api_key='biom_live_test')

	mock_response = MagicMock()
	mock_response.status_code = 200
	mock_response.ok = True
	mock_response.json.return_value = {
		'fields': [
			{'key': 'patientId', 'label': 'Patient ID', 'type': 'NUMBER', 'operators': ['equals', 'gt', 'lt']},
			{'key': 'age', 'label': 'Age', 'type': 'NUMBER', 'operators': ['equals', 'gt', 'between']},
			{'key': 'gender', 'label': 'Gender', 'type': 'TEXT', 'operators': ['equals', 'contains']},
		],
		'typeOperators': {'TEXT': ['equals', 'contains']},
	}

	with patch.object(client.session, 'request', return_value=mock_response):
		catalog = client.fields()
		assert isinstance(catalog, FieldCatalog)
		assert len(catalog) == 3
		assert 'age' in catalog.keys()
		assert catalog['age'].type == 'NUMBER'

		df = catalog.to_dataframe()
		assert isinstance(df, pd.DataFrame)
		assert len(df) == 3
		assert 'operators' in df.columns
		assert '<table' in catalog._repr_html_()


def test_datasets_discovery():
	client = BiomClient(api_key='biom_live_test')

	mock_response = MagicMock()
	mock_response.status_code = 200
	mock_response.ok = True
	mock_response.json.return_value = {
		'datasets': [
			{
				'id': 1,
				'name': 'Cardio Cohort 2024',
				'reference': 'CV-2024',
				'category': 'CLINICAL',
				'status': 'ACTIVE',
				'version': 1,
				'recordCount': 250,
				'variableCount': 12,
				'createdAt': '2024-01-01',
			},
			{
				'id': 2,
				'name': 'Diabetes Cohort 2024',
				'reference': 'DB-2024',
				'category': 'OBSERVATIONAL',
				'status': 'ACTIVE',
				'version': 2,
				'recordCount': 180,
				'variableCount': 24,
				'createdAt': '2024-02-01',
			},
		],
	}

	with patch.object(client.session, 'request', return_value=mock_response):
		catalog = client.datasets()
		assert isinstance(catalog, DatasetCatalog)
		assert len(catalog) == 2

		# Lookup by integer ID
		d1 = catalog[1]
		assert d1.name == 'Cardio Cohort 2024'
		assert d1.record_count == 250

		# Lookup by string name
		d2 = catalog['Diabetes Cohort 2024']
		assert d2.id == 2

		df = catalog.to_dataframe()
		assert len(df) == 2
		assert 'records' in df.columns


def test_variables_discovery():
	client = BiomClient(api_key='biom_live_test')

	mock_response = MagicMock()
	mock_response.status_code = 200
	mock_response.ok = True
	mock_response.json.return_value = {
		'dataset': {'id': 1, 'name': 'Cardio Cohort 2024'},
		'variables': [
			{'id': 10, 'name': 'Fasting Glucose', 'type': 'NUMBER', 'operators': ['gt', 'lt'], 'notes': 'mg/dL'},
			{'id': 11, 'name': 'Smoker', 'type': 'BOOLEAN', 'operators': ['equals'], 'notes': ''},
		],
	}

	with patch.object(client.session, 'request', return_value=mock_response):
		catalog = client.variables(dataset_id=1)
		assert isinstance(catalog, VariableCatalog)
		assert len(catalog) == 2
		assert 'Fasting Glucose' in catalog.names()
		assert catalog['Fasting Glucose'].notes == 'mg/dL'

		df = catalog.to_dataframe()
		assert len(df) == 2
		assert 'operators' in df.columns


def test_search_variables():
	client = BiomClient(api_key='biom_live_test')

	mock_response = MagicMock()
	mock_response.status_code = 200
	mock_response.ok = True
	mock_response.json.return_value = {
		'variables': [
			{'name': 'Fasting Glucose', 'type': 'NUMBER', 'operators': ['gt', 'lt']},
		],
	}

	with patch.object(client.session, 'request', return_value=mock_response):
		results = client.search_variables('gluc')
		assert len(results) == 1
		assert results[0]['name'] == 'Fasting Glucose'

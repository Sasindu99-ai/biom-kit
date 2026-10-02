from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from biom import BiomClient, F
from biom.exceptions import BiomFilterError
from biom.query import compile_filters, parse_kwargs_filters


def test_f_expression_operators():
	r1 = F('age') >= 18
	assert r1.to_dict() == {'field': 'age', 'operator': 'gte', 'value': 18, 'scope': 'auto'}

	r2 = F('gender') == 'Female'
	assert r2.to_dict() == {'field': 'gender', 'operator': 'equals', 'value': 'Female', 'scope': 'auto'}

	r3 = F('Glucose') > 110
	assert r3.to_dict() == {'field': 'Glucose', 'operator': 'gt', 'value': 110, 'scope': 'auto'}

	r4 = F('Glucose') < 200
	assert r4.to_dict() == {'field': 'Glucose', 'operator': 'lt', 'value': 200, 'scope': 'auto'}

	r5 = F('age').between(20, 60)
	assert r5.to_dict() == {'field': 'age', 'operator': 'between', 'value': 20, 'valueTo': 60, 'scope': 'auto'}

	r6 = F('notes').contains('hypertension')
	assert r6.to_dict() == {'field': 'notes', 'operator': 'contains', 'value': 'hypertension', 'scope': 'auto'}

	r7 = F('reference').startswith('CV-')
	assert r7.to_dict() == {'field': 'reference', 'operator': 'starts_with', 'value': 'CV-', 'scope': 'auto'}

	r8 = F('latitude').is_empty()
	assert r8.to_dict() == {'field': 'latitude', 'operator': 'is_empty', 'value': None, 'scope': 'auto'}


def test_f_expression_unsupported_inequality():
	with pytest.raises(BiomFilterError):
		_ = F('age') != 18


def test_parse_kwargs_filters():
	rules = parse_kwargs_filters(
		age__gte=18,
		age__lte=65,
		gender='Female',
		glucose__gt=100,
		testedDate__between=('2024-01-01', '2024-12-31'),
	)
	dicts = [r.to_dict() for r in rules]
	assert {'field': 'age', 'operator': 'gte', 'value': 18, 'scope': 'auto'} in dicts
	assert {'field': 'age', 'operator': 'lte', 'value': 65, 'scope': 'auto'} in dicts
	assert {'field': 'gender', 'operator': 'equals', 'value': 'Female', 'scope': 'auto'} in dicts
	assert {'field': 'glucose', 'operator': 'gt', 'value': 100, 'scope': 'auto'} in dicts
	assert {
		'field': 'testedDate',
		'operator': 'between',
		'value': '2024-01-01',
		'valueTo': '2024-12-31',
		'scope': 'auto',
	} in dicts


def test_compile_filters_combined():
	compiled = compile_filters(
		F('Glucose') > 115,
		{'field': 'Smoker', 'operator': 'equals', 'value': True},
		age__gte=21,
	)
	assert len(compiled) == 3
	fields = [c['field'] for c in compiled]
	assert 'Glucose' in fields
	assert 'Smoker' in fields
	assert 'age' in fields


def test_dataset_fluent_chaining_and_execution():
	client = BiomClient(api_key='biom_live_test')

	mock_response = MagicMock()
	mock_response.status_code = 200
	mock_response.ok = True
	mock_response.json.return_value = {
		'meta': {'totalRecords': 1, 'returnedRecords': 1, 'page': 1, 'limit': 1000},
		'columns': [
			{'name': 'patientId', 'type': 'NUMBER'},
			{'name': 'age', 'type': 'NUMBER'},
			{'name': 'Glucose', 'type': 'NUMBER'},
		],
		'records': [
			{'patientId': 101, 'age': 42, 'Glucose': 118.5},
		],
	}

	with patch.object(client.session, 'request', return_value=mock_response) as mock_req:
		df = (
			client.dataset(1)
			.filter(age__gte=40)
			.filter('Glucose', gt=100)
			.select('patientId', 'age', 'Glucose')
			.sort_by('age', ascending=False)
			.page(1, limit=500)
			.to_dataframe()
		)

		assert isinstance(df, pd.DataFrame)
		assert len(df) == 1
		assert df.iloc[0]['Glucose'] == 118.5

		# Verify sent payload to backend
		call_kwargs = mock_req.call_args[1]
		payload = call_kwargs['json']
		assert payload['study_ids'] == [1]
		assert payload['limit'] == 500
		assert payload['sortField'] == 'age'
		assert payload['sortDirection'] == 'desc'
		assert payload['fields'] == ['patientId', 'age', 'Glucose']

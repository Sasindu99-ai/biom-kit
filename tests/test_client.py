from unittest.mock import MagicMock, patch

import biom
import pytest
from biom import BiomClient
from biom.exceptions import BiomAPIError, BiomAuthError, BiomNotFoundError


def test_client_init_and_headers():
	client = BiomClient(api_key='biom_live_testkey123', base_url='https://api.biom.org')
	assert client.api_key == 'biom_live_testkey123'
	assert client.base_url == 'https://api.biom.org'
	headers = client._headers()
	assert headers['X-API-Key'] == 'biom_live_testkey123'
	assert headers['Content-Type'] == 'application/json'


def test_client_env_var_fallback(monkeypatch):
	monkeypatch.setenv('BIOM_API_KEY', 'biom_live_env_key')
	monkeypatch.setenv('BIOM_BASE_URL', 'https://env.biom.org')
	biom.set_api_key(None)
	biom.set_base_url(None)

	client = BiomClient()
	assert client.api_key == 'biom_live_env_key'
	assert client.base_url == 'https://env.biom.org'


def test_login_updates_config():
	biom.login(api_key='biom_live_new_key', base_url='https://custom.biom.org')
	c = biom.client()
	assert c.api_key == 'biom_live_new_key'
	assert c.base_url == 'https://custom.biom.org'


def test_client_verify_success():
	client = BiomClient(api_key='biom_live_valid')

	mock_response = MagicMock()
	mock_response.status_code = 200
	mock_response.ok = True
	mock_response.json.return_value = {
		'status': 'success',
		'user': {'username': 'dr_smith', 'isStaff': True},
	}

	with patch.object(client.session, 'request', return_value=mock_response):
		user = client.verify()
		assert user['username'] == 'dr_smith'
		assert user['isStaff'] is True


def test_client_auth_error_on_401():
	client = BiomClient(api_key='biom_live_invalid')

	mock_response = MagicMock()
	mock_response.status_code = 401
	mock_response.ok = False
	mock_response.json.return_value = {'detail': 'Invalid or revoked API key'}

	with patch.object(client.session, 'request', return_value=mock_response):
		with pytest.raises(BiomAuthError) as exc_info:
			client.verify()
		assert 'Authentication failed' in str(exc_info.value)


def test_client_not_found_on_404():
	client = BiomClient(api_key='biom_live_key')

	mock_response = MagicMock()
	mock_response.status_code = 404
	mock_response.ok = False

	with patch.object(client.session, 'request', return_value=mock_response), pytest.raises(BiomNotFoundError):
		client._request('GET', '/api/v1/missing')


def test_client_api_error_on_500():
	client = BiomClient(api_key='biom_live_key')

	mock_response = MagicMock()
	mock_response.status_code = 500
	mock_response.ok = False
	mock_response.json.return_value = {'error': 'Internal database failure'}

	with patch.object(client.session, 'request', return_value=mock_response), pytest.raises(BiomAPIError):
		client._request('GET', '/api/v1/crash')

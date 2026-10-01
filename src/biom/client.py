"""
HTTP Client for the BIOM platform.
Handles API key authentication, request dispatching, and response parsing.
"""

from typing import Any
import requests

from .config import get_api_key, get_base_url, get_timeout
from .dataset import Dataset
from .exceptions import BiomAPIError, BiomAuthError, BiomNotFoundError
from .models import (
	DatasetCatalog,
	DatasetInfo,
	FieldCatalog,
	FieldInfo,
	QueryResult,
	VariableCatalog,
	VariableInfo,
)
from .query import compile_filters

__all__ = ['BiomClient']


class BiomClient:
	"""
	Main client for interacting with the BIOM platform.

	Args:
	    api_key: Optional API key (defaults to BIOM_API_KEY environment variable).
	    base_url: Optional base URL (defaults to BIOM_BASE_URL environment variable or local server).
	    timeout: Request timeout in seconds.
	"""

	def __init__(
		self,
		api_key: str | None = None,
		base_url: str | None = None,
		timeout: float | None = None,
	):
		self.api_key = api_key or get_api_key()
		self.base_url = (base_url or get_base_url()).rstrip('/')
		self.timeout = timeout or get_timeout()
		self.session = requests.Session()

	def _headers(self) -> dict[str, str]:
		headers = {
			'Content-Type': 'application/json',
			'Accept': 'application/json',
		}
		if self.api_key:
			headers['X-API-Key'] = self.api_key
		return headers

	def _request(
		self,
		method: str,
		endpoint: str,
		params: dict[str, Any] | None = None,
		json_data: dict[str, Any] | None = None,
	) -> dict[str, Any]:
		url = f'{self.base_url}/{endpoint.lstrip("/")}'
		headers = self._headers()

		try:
			response = self.session.request(
				method=method,
				url=url,
				headers=headers,
				params=params,
				json=json_data,
				timeout=self.timeout,
			)
		except requests.RequestException as e:
			raise BiomAPIError(f'Failed to connect to BIOM server at {url}: {e}') from e

		if response.status_code in (401, 403):
			msg = 'Authentication failed. Please verify your API key using biom.login("your_key").'
			try:
				detail = response.json().get('detail') or response.json().get('message')
				if detail:
					msg = f'Authentication failed: {detail}'
			except Exception:
				pass
			raise BiomAuthError(msg)

		if response.status_code == 404:
			raise BiomNotFoundError(f'Requested resource at {url} was not found (404).')

		if not response.ok:
			try:
				err_payload = response.json()
			except Exception:
				err_payload = {'text': response.text}
			raise BiomAPIError(
				f'BIOM API error ({response.status_code}): {err_payload}',
				status_code=response.status_code,
				response_data=err_payload,
			)

		try:
			return response.json()
		except Exception as e:
			raise BiomAPIError(f'Failed to parse JSON response from {url}: {e}') from e

	def verify(self) -> dict[str, Any]:
		"""
		Verifies the active API key and returns authenticated user details.
		"""
		data = self._request('GET', '/api/v1/kit/auth/verify')
		return data.get('user', {})

	def fields(self) -> FieldCatalog:
		"""
		Returns catalog of all filterable patient profile fields (known fields),
		including their data types, human labels, and supported filter operators.
		"""
		data = self._request('GET', '/api/v1/kit/fields')
		fields_list = []
		for f in data.get('fields', []):
			fields_list.append(
				FieldInfo(
					key=f['key'],
					label=f.get('label', f['key']),
					field_type=f.get('type', 'TEXT'),
					operators=f.get('operators', []),
					description=f.get('description', ''),
				)
			)
		return FieldCatalog(fields_list)

	def datasets(self, search: str = '') -> DatasetCatalog:
		"""
		Returns catalog of available datasets/studies.
		"""
		params = {'search': search} if search else None
		data = self._request('GET', '/api/v1/kit/datasets', params=params)
		datasets_list = [DatasetInfo(d) for d in data.get('datasets', [])]
		return DatasetCatalog(datasets_list)

	def dataset(self, id_or_name: int | str) -> Dataset:
		"""
		Returns a fluent Dataset builder for a specific dataset ID or name.
		"""
		if isinstance(id_or_name, int):
			return Dataset(self, dataset_id=id_or_name)

		# If string, lookup in datasets catalog
		catalog = self.datasets()
		matched = catalog[id_or_name]
		return Dataset(self, dataset_id=matched.id, dataset_name=matched.name)

	def variables(self, dataset_id: int) -> VariableCatalog:
		"""
		Returns catalog of variables defined for a specific dataset.
		"""
		data = self._request('GET', f'/api/v1/kit/datasets/{dataset_id}/variables')
		dataset_name = data.get('dataset', {}).get('name', f'Dataset #{dataset_id}')
		var_list = [VariableInfo(v) for v in data.get('variables', [])]
		return VariableCatalog(dataset_name, var_list)

	def search_variables(self, query: str = '', limit: int = 50) -> list[dict[str, Any]]:
		"""
		Searches for variable names across datasets.
		"""
		params = {'q': query, 'limit': limit}
		data = self._request('GET', '/api/v1/kit/variables/search', params=params)
		return data.get('variables', [])

	def query(
		self,
		dataset: int | str | None = None,
		datasets: list[int | str] | None = None,
		filters: list[Any] | None = None,
		filter_logic: str = 'AND',
		fields: list[str] | None = None,
		page: int = 1,
		limit: int = 5000,
		sort_field: str = 'created_at',
		sort_direction: str = 'desc',
		**kwargs,
	) -> QueryResult:
		"""
		Executes structured query and returns QueryResult (convertible to pandas.DataFrame).
		"""
		study_ids = []
		if dataset is not None:
			if isinstance(dataset, int):
				study_ids.append(dataset)
			else:
				study_ids.append(self.dataset(dataset).dataset_id)

		if datasets:
			for item in datasets:
				if isinstance(item, int):
					study_ids.append(item)
				else:
					study_ids.append(self.dataset(item).dataset_id)

		compiled_rules = compile_filters(*(filters or []), **kwargs)

		payload = {
			'study_ids': study_ids,
			'filters': compiled_rules,
			'filterLogic': 'OR' if filter_logic.upper() == 'OR' else 'AND',
			'fields': fields,
			'page': page,
			'limit': limit,
			'sortField': sort_field,
			'sortDirection': sort_direction,
		}

		data = self._request('POST', '/api/v1/kit/query', json_data=payload)
		return QueryResult(data)

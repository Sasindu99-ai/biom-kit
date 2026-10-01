"""
BIOM Kit (biom-kit) - Python client and data science toolkit for the BIOM platform.
"""

from typing import Any

from . import tools
from .client import BiomClient
from .config import (
	get_api_key,
	get_base_url,
	get_timeout,
	login,
	set_api_key,
	set_base_url,
	set_timeout,
)
from .dataset import Dataset
from .exceptions import (
	BiomAPIError,
	BiomAuthError,
	BiomError,
	BiomFilterError,
	BiomNotFoundError,
)
from .models import (
	DatasetCatalog,
	DatasetInfo,
	FieldCatalog,
	FieldInfo,
	QueryResult,
	VariableCatalog,
	VariableInfo,
)
from .query import F

__version__ = '0.1.0'

__all__ = [
	'BiomAPIError',
	'BiomAuthError',
	'BiomClient',
	'BiomError',
	'BiomFilterError',
	'BiomNotFoundError',
	'Dataset',
	'DatasetCatalog',
	'DatasetInfo',
	'F',
	'FieldCatalog',
	'FieldInfo',
	'QueryResult',
	'VariableCatalog',
	'VariableInfo',
	'__version__',
	'client',
	'dataset',
	'datasets',
	'fields',
	'get_api_key',
	'get_base_url',
	'get_timeout',
	'login',
	'query',
	'search_variables',
	'set_api_key',
	'set_base_url',
	'set_timeout',
	'tools',
	'variables',
]

_default_client: BiomClient | None = None


def client() -> BiomClient:
	"""
	Returns the default BiomClient instance, lazily configured.
	"""
	global _default_client
	if _default_client is None:
		_default_client = BiomClient()
	else:
		# Update credentials if changed via biom.login() or environment
		_default_client.api_key = get_api_key()
		_default_client.base_url = get_base_url()
	return _default_client


def fields() -> FieldCatalog:
	"""
	Discover all known patient profile fields with their types and supported operators.
	"""
	return client().fields()


def datasets(search: str = '') -> DatasetCatalog:
	"""
	List all available datasets/studies.
	"""
	return client().datasets(search=search)


def dataset(id_or_name: int | str) -> Dataset:
	"""
	Returns a fluent chainable Dataset builder for filtering and querying.
	"""
	return client().dataset(id_or_name)


def variables(dataset_id: int) -> VariableCatalog:
	"""
	Discover all variables defined within a specific dataset.
	"""
	return client().variables(dataset_id)


def search_variables(query: str = '', limit: int = 50) -> list[dict[str, Any]]:
	"""
	Search for variables across datasets by query.
	"""
	return client().search_variables(query=query, limit=limit)


def query(
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
	Directly execute a structured query across one or more datasets.
	"""
	return client().query(
		dataset=dataset,
		datasets=datasets,
		filters=filters,
		filter_logic=filter_logic,
		fields=fields,
		page=page,
		limit=limit,
		sort_field=sort_field,
		sort_direction=sort_direction,
		**kwargs,
	)

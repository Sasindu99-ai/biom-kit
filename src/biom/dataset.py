"""
Fluent Dataset wrapper supporting chainable queries, column projections, and DataFrame conversion.
"""

from typing import TYPE_CHECKING, Any

import pandas as pd

from .models import DatasetInfo, QueryResult, VariableCatalog
from .query import FilterRule, compile_filters

if TYPE_CHECKING:
	from .client import BiomClient

__all__ = ['Dataset']


class Dataset:
	"""
	Fluent interface for inspecting and querying a specific BIOM dataset.

	Usage:
	    ds = biom.dataset(1)
	    df = (
	        ds.filter(age__gte=18, age__lte=65)
	        .filter(gender="Female")
	        .filter("Glucose", gt=110)
	        .sort_by("age")
	        .to_dataframe()
	    )
	"""

	def __init__(self, client: 'BiomClient', dataset_id: int, dataset_name: str | None = None):
		self.client = client
		self.dataset_id = dataset_id
		self._dataset_name = dataset_name
		self._filters: list[dict[str, Any]] = []
		self._filter_logic: str = 'AND'
		self._fields: list[str] | None = None
		self._sort_field: str = 'created_at'
		self._sort_direction: str = 'desc'
		self._page: int = 1
		self._limit: int = 5000

	def _clone(self) -> 'Dataset':
		clone = Dataset(self.client, self.dataset_id, self._dataset_name)
		clone._filters = list(self._filters)
		clone._filter_logic = self._filter_logic
		clone._fields = list(self._fields) if self._fields is not None else None
		clone._sort_field = self._sort_field
		clone._sort_direction = self._sort_direction
		clone._page = self._page
		clone._limit = self._limit
		return clone

	def filter(self, *args, **kwargs) -> 'Dataset':
		"""
		Add filter conditions (AND logic).
		Supports:
		    .filter(age__gte=18, gender="Female")
		    .filter(F("Glucose") > 110)
		    .filter("Glucose", gt=110)  # Shorthand for variables with spaces
		"""
		clone = self._clone()
		clone._filter_logic = 'AND'

		# Support shorthand: .filter("Glucose", gt=110)
		if len(args) == 1 and isinstance(args[0], str) and kwargs:
			field_name = args[0]
			for op, val in kwargs.items():
				val_from, val_to = (val[0], val[1]) if (op == 'between' and isinstance(val, (list, tuple))) else (val, None)
				clone._filters.append(
					FilterRule(field_name, op, val_from, value_to=val_to).to_dict(),
				)
			return clone

		compiled = compile_filters(*args, **kwargs)
		clone._filters.extend(compiled)
		return clone

	def filter_or(self, *args, **kwargs) -> 'Dataset':
		"""
		Set filter logic to OR and add conditions.
		"""
		clone = self._clone()
		clone._filter_logic = 'OR'
		compiled = compile_filters(*args, **kwargs)
		clone._filters.extend(compiled)
		return clone

	def select(self, *fields: str) -> 'Dataset':
		"""
		Project only specific fields or variables in output.
		"""
		clone = self._clone()
		clone._fields = list(fields)
		return clone

	def sort_by(self, field: str, ascending: bool = True) -> 'Dataset':
		"""
		Sort query results by a field.
		"""
		clone = self._clone()
		clone._sort_field = field
		clone._sort_direction = 'asc' if ascending else 'desc'
		return clone

	def page(self, page_num: int = 1, limit: int = 5000) -> 'Dataset':
		"""
		Configure pagination.
		"""
		clone = self._clone()
		clone._page = max(int(page_num), 1)
		clone._limit = max(int(limit), 1)
		return clone

	def execute(self) -> QueryResult:
		"""
		Executes the query and returns a QueryResult container.
		"""
		return self.client.query(
			dataset=self.dataset_id,
			filters=self._filters,
			filter_logic=self._filter_logic,
			fields=self._fields,
			page=self._page,
			limit=self._limit,
			sort_field=self._sort_field,
			sort_direction=self._sort_direction,
		)

	def to_dataframe(self) -> pd.DataFrame:
		"""
		Executes query and returns data directly as a pandas DataFrame.
		"""
		return self.execute().to_dataframe()

	def to_records(self) -> list[dict[str, Any]]:
		"""
		Executes query and returns records as a list of dictionaries.
		"""
		return self.execute().to_records()

	def variables(self) -> VariableCatalog:
		"""
		Inspect all variables belonging to this dataset.
		"""
		return self.client.variables(self.dataset_id)

	def info(self) -> DatasetInfo:
		"""
		Retrieve metadata details about this dataset.
		"""
		catalog = self.client.datasets()
		return catalog[self.dataset_id]

	def __repr__(self) -> str:
		name_part = f' "{self._dataset_name}"' if self._dataset_name else ''
		return f'<Dataset: #{self.dataset_id}{name_part} ({len(self._filters)} active filters)>'

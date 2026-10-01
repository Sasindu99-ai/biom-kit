"""
Data models and display containers for biom-kit.
Provides interactive DataFrame conversions and rich HTML representations for Jupyter/Colab.
"""

from typing import Any

import pandas as pd

__all__ = [
	'DatasetCatalog',
	'DatasetInfo',
	'FieldCatalog',
	'FieldInfo',
	'QueryResult',
	'VariableCatalog',
	'VariableInfo',
]


class FieldInfo:

	def __init__(self, key: str, label: str, field_type: str, operators: list[str], description: str = ''):
		self.key = key
		self.label = label
		self.type = field_type
		self.operators = operators
		self.description = description

	def to_dict(self) -> dict[str, Any]:
		return {
			'key': self.key,
			'label': self.label,
			'type': self.type,
			'operators': ', '.join(self.operators),
			'description': self.description,
		}

	def __repr__(self) -> str:
		return f'<FieldInfo: {self.key} ({self.type})>'


class FieldCatalog:

	def __init__(self, fields: list[FieldInfo]):
		self._fields = fields
		self._by_key = {f.key.lower(): f for f in fields}

	def __len__(self) -> int:
		return len(self._fields)

	def __iter__(self):
		return iter(self._fields)

	def __getitem__(self, item: int | str) -> FieldInfo:
		if isinstance(item, int):
			return self._fields[item]
		key_l = str(item).lower()
		if key_l in self._by_key:
			return self._by_key[key_l]
		raise KeyError(f'Field "{item}" not found in catalog.')

	def keys(self) -> list[str]:
		return [f.key for f in self._fields]

	def to_dataframe(self) -> pd.DataFrame:
		return pd.DataFrame([f.to_dict() for f in self._fields])

	def _repr_html_(self) -> str:
		return self.to_dataframe()._repr_html_()

	def __repr__(self) -> str:
		return f'<FieldCatalog: {len(self._fields)} profile fields>'

	def __str__(self) -> str:
		return self.to_dataframe().to_string(index=False)


class DatasetInfo:

	def __init__(self, data: dict[str, Any]):
		self.id: int = data.get('id')
		self.name: str = data.get('name', '')
		self.reference: str = data.get('reference', '')
		self.category: str = data.get('category', '')
		self.status: str = data.get('status', '')
		self.version: int = data.get('version', 1)
		self.record_count: int = data.get('recordCount', 0)
		self.variable_count: int = data.get('variableCount', 0)
		self.created_at: str = data.get('createdAt', '')

	def to_dict(self) -> dict[str, Any]:
		return {
			'id': self.id,
			'name': self.name,
			'reference': self.reference,
			'category': self.category,
			'status': self.status,
			'records': self.record_count,
			'variables': self.variable_count,
			'createdAt': self.created_at,
		}

	def __repr__(self) -> str:
		return f'<DatasetInfo: #{self.id} "{self.name}">'


class DatasetCatalog:

	def __init__(self, datasets: list[DatasetInfo]):
		self._datasets = datasets

	def __len__(self) -> int:
		return len(self._datasets)

	def __iter__(self):
		return iter(self._datasets)

	def __getitem__(self, item: int | str) -> DatasetInfo:
		if isinstance(item, int):
			for d in self._datasets:
				if d.id == item:
					return d
			if 0 <= item < len(self._datasets):
				return self._datasets[item]
		item_l = str(item).lower()
		for d in self._datasets:
			if d.name.lower() == item_l or d.reference.lower() == item_l:
				return d
		raise KeyError(f'Dataset "{item}" not found in catalog.')

	def to_dataframe(self) -> pd.DataFrame:
		return pd.DataFrame([d.to_dict() for d in self._datasets])

	def _repr_html_(self) -> str:
		return self.to_dataframe()._repr_html_()

	def __repr__(self) -> str:
		return f'<DatasetCatalog: {len(self._datasets)} datasets>'

	def __str__(self) -> str:
		return self.to_dataframe().to_string(index=False)


class VariableInfo:

	def __init__(self, data: dict[str, Any]):
		self.id: int | None = data.get('id')
		self.name: str = data.get('name', '')
		self.type: str = data.get('type', 'TEXT')
		self.field: str = data.get('field', 'TEXT')
		self.operators: list[str] = data.get('operators', [])
		self.notes: str = data.get('notes', '')

	def to_dict(self) -> dict[str, Any]:
		return {
			'name': self.name,
			'type': self.type,
			'operators': ', '.join(self.operators),
			'notes': self.notes,
		}

	def __repr__(self) -> str:
		return f'<VariableInfo: "{self.name}" ({self.type})>'


class VariableCatalog:

	def __init__(self, dataset_name: str, variables: list[VariableInfo]):
		self.dataset_name = dataset_name
		self._variables = variables
		self._by_name = {v.name.lower(): v for v in variables}

	def __len__(self) -> int:
		return len(self._variables)

	def __iter__(self):
		return iter(self._variables)

	def __getitem__(self, item: int | str) -> VariableInfo:
		if isinstance(item, int):
			return self._variables[item]
		item_l = str(item).lower()
		if item_l in self._by_name:
			return self._by_name[item_l]
		raise KeyError(f'Variable "{item}" not found in catalog.')

	def names(self) -> list[str]:
		return [v.name for v in self._variables]

	def to_dataframe(self) -> pd.DataFrame:
		return pd.DataFrame([v.to_dict() for v in self._variables])

	def _repr_html_(self) -> str:
		return self.to_dataframe()._repr_html_()

	def __repr__(self) -> str:
		return f'<VariableCatalog: {len(self._variables)} variables in "{self.dataset_name}">'

	def __str__(self) -> str:
		return self.to_dataframe().to_string(index=False)


class QueryResult:

	def __init__(self, data: dict[str, Any]):
		self.meta: dict[str, Any] = data.get('meta', {})
		self.columns: list[dict[str, Any]] = data.get('columns', [])
		self.records: list[dict[str, Any]] = data.get('records', [])
		self._df: pd.DataFrame | None = None

	def __len__(self) -> int:
		return len(self.records)

	def to_records(self) -> list[dict[str, Any]]:
		return self.records

	def to_dataframe(self) -> pd.DataFrame:
		if self._df is None:
			if not self.records:
				col_names = [c['name'] for c in self.columns]
				self._df = pd.DataFrame(columns=col_names)
			else:
				self._df = pd.DataFrame(self.records)
		return self._df.copy()

	@property
	def total_records(self) -> int:
		return self.meta.get('totalRecords', len(self.records))

	def _repr_html_(self) -> str:
		df = self.to_dataframe()
		summary = f'<p><strong>QueryResult</strong>: {len(df)} records returned (Total matching: {self.total_records})</p>'
		return summary + df.head(10)._repr_html_()

	def __repr__(self) -> str:
		return f'<QueryResult: {len(self.records)} records (total: {self.total_records})>'

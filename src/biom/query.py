"""
Query expression builder and filter compiler for biom-kit.
Supports both declarative F expressions and keyword-suffix filter rules.
"""

from typing import Any

from .exceptions import BiomFilterError

__all__ = ['F', 'FilterRule', 'compile_filters', 'parse_kwargs_filters']


class FilterRule:

	def __init__(
		self,
		field: str,
		operator: str,
		value: Any = None,
		value_to: Any = None,
		scope: str = 'auto',
	):
		self.field = field
		self.operator = operator
		self.value = value
		self.value_to = value_to
		self.scope = scope

	def to_dict(self) -> dict[str, Any]:
		rule = {
			'field': self.field,
			'operator': self.operator,
			'value': self.value,
			'scope': self.scope,
		}
		if self.value_to is not None:
			rule['valueTo'] = self.value_to
		return rule

	def __repr__(self) -> str:
		if self.value_to is not None:
			return f'<FilterRule: {self.field} {self.operator} [{self.value}, {self.value_to}]>'
		return f'<FilterRule: {self.field} {self.operator} {self.value}>'


class F:
	"""
	Filter expression builder for biom-kit.

	Examples:
	    F("age") >= 18
	    F("gender") == "Female"
	    F("Glucose") > 110
	    F("testedDate").between("2024-01-01", "2024-12-31")
	    F("notes").contains("hypertension")
	"""

	def __init__(self, field_name: str, scope: str = 'auto'):
		self.field_name = str(field_name).strip()
		self.scope = scope

	def __eq__(self, other: object) -> FilterRule:
		return FilterRule(self.field_name, 'equals', other, scope=self.scope)

	def __ne__(self, other: object) -> FilterRule:
		# Since BIOM backend doesn't have direct neq, equals with inverted logic or custom
		raise BiomFilterError(
			'Inequality (!=) is not directly supported by backend operators. '
			'Use specific comparison operators (gt, lt) or is_empty/is_not_empty.',
		)

	def __gt__(self, other: Any) -> FilterRule:
		return FilterRule(self.field_name, 'gt', other, scope=self.scope)

	def __ge__(self, other: Any) -> FilterRule:
		return FilterRule(self.field_name, 'gte', other, scope=self.scope)

	def __lt__(self, other: Any) -> FilterRule:
		return FilterRule(self.field_name, 'lt', other, scope=self.scope)

	def __le__(self, other: Any) -> FilterRule:
		return FilterRule(self.field_name, 'lte', other, scope=self.scope)

	def contains(self, text: str) -> FilterRule:
		return FilterRule(self.field_name, 'contains', text, scope=self.scope)

	def startswith(self, text: str) -> FilterRule:
		return FilterRule(self.field_name, 'starts_with', text, scope=self.scope)

	def endswith(self, text: str) -> FilterRule:
		return FilterRule(self.field_name, 'ends_with', text, scope=self.scope)

	def between(self, val_from: Any, val_to: Any) -> FilterRule:
		return FilterRule(self.field_name, 'between', val_from, value_to=val_to, scope=self.scope)

	def before(self, date_val: Any) -> FilterRule:
		return FilterRule(self.field_name, 'before', date_val, scope=self.scope)

	def after(self, date_val: Any) -> FilterRule:
		return FilterRule(self.field_name, 'after', date_val, scope=self.scope)

	def is_empty(self) -> FilterRule:
		return FilterRule(self.field_name, 'is_empty', scope=self.scope)

	def is_not_empty(self) -> FilterRule:
		return FilterRule(self.field_name, 'is_not_empty', scope=self.scope)

	def __repr__(self) -> str:
		return f'<F: "{self.field_name}">'


_SUFFIX_MAP = {
	'__gte': 'gte',
	'__gt': 'gt',
	'__lte': 'lte',
	'__lt': 'lt',
	'__contains': 'contains',
	'__icontains': 'contains',
	'__startswith': 'starts_with',
	'__endswith': 'ends_with',
	'__before': 'before',
	'__after': 'after',
	'__between': 'between',
	'__is_empty': 'is_empty',
	'__is_not_empty': 'is_not_empty',
	'__exact': 'equals',
	'__equals': 'equals',
}


def parse_kwargs_filters(**kwargs) -> list[FilterRule]:
	"""
	Parses Django-style keyword arguments into FilterRules.
	Examples:
	    age__gte=18
	    gender="Female"
	    testedDate__between=("2024-01-01", "2024-12-31")
	"""
	rules = []
	for raw_key, value in kwargs.items():
		operator = 'equals'
		field = raw_key
		value_to = None

		for suffix, op in _SUFFIX_MAP.items():
			if raw_key.endswith(suffix):
				field = raw_key[:-len(suffix)]
				operator = op
				break

		if operator == 'between':
			if isinstance(value, (list, tuple)) and len(value) == 2:
				val_from, value_to = value
				rules.append(FilterRule(field, operator, val_from, value_to=value_to))
			else:
				raise BiomFilterError(
					f'Filter "{raw_key}" with operator "between" requires a 2-tuple (val_from, val_to).',
				)
		elif operator in ('is_empty', 'is_not_empty'):
			rules.append(FilterRule(field, operator))
		else:
			rules.append(FilterRule(field, operator, value))

	return rules


def compile_filters(*rules, **kwargs) -> list[dict[str, Any]]:
	"""
	Compiles a mixture of FilterRules and kwargs into a list of serialized filter dictionaries.
	"""
	all_rules: list[FilterRule] = []

	for item in rules:
		if isinstance(item, FilterRule):
			all_rules.append(item)
		elif isinstance(item, dict):
			all_rules.append(
				FilterRule(
					field=item.get('field', item.get('fieldKey', '')),
					operator=item.get('operator', 'equals'),
					value=item.get('value'),
					value_to=item.get('valueTo'),
					scope=item.get('scope', 'auto'),
				),
			)
		else:
			raise BiomFilterError(f'Unsupported filter expression: {item}')

	if kwargs:
		all_rules.extend(parse_kwargs_filters(**kwargs))

	return [rule.to_dict() for rule in all_rules]

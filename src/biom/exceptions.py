"""
Custom exceptions for biom-kit.
"""

__all__ = [
	'BiomAPIError',
	'BiomAuthError',
	'BiomError',
	'BiomFilterError',
	'BiomNotFoundError',
]


class BiomError(Exception):
	"""Base exception for all biom-kit errors."""
	pass


class BiomAuthError(BiomError):
	"""Raised when authentication fails (missing, invalid, or revoked API key)."""
	pass


class BiomNotFoundError(BiomError):
	"""Raised when a requested resource (dataset, variable, etc.) does not exist."""
	pass


class BiomFilterError(BiomError):
	"""Raised when invalid filtering parameters or operators are specified."""
	pass


class BiomAPIError(BiomError):
	"""Raised when the BIOM API responds with an unexpected error status."""

	def __init__(self, message: str, status_code: int | None = None, response_data: dict | None = None):
		super().__init__(message)
		self.status_code = status_code
		self.response_data = response_data or {}

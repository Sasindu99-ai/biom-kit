"""
Configuration management for biom-kit.
Supports environment variables BIOM_API_KEY and BIOM_BASE_URL.
"""

import os

__all__ = [
	'get_api_key',
	'get_base_url',
	'get_timeout',
	'login',
	'set_api_key',
	'set_base_url',
	'set_timeout',
]

_DEFAULT_BASE_URL = 'https://biom.arceion.com'
_DEFAULT_TIMEOUT = 30.0

_api_key: str | None = None
_base_url: str | None = None
_timeout: float = _DEFAULT_TIMEOUT


def get_api_key() -> str | None:
	global _api_key
	if _api_key:
		return _api_key
	return os.environ.get('BIOM_API_KEY')


def set_api_key(key: str | None) -> None:
	global _api_key
	_api_key = key.strip() if key else None


def get_base_url() -> str:
	global _base_url
	if _base_url:
		return _base_url
	env_url = os.environ.get('BIOM_BASE_URL')
	if env_url:
		return env_url.rstrip('/')
	return _DEFAULT_BASE_URL


def set_base_url(url: str | None) -> None:
	global _base_url
	_base_url = url.rstrip('/') if url else None


def get_timeout() -> float:
	global _timeout
	return _timeout


def set_timeout(seconds: float) -> None:
	global _timeout
	_timeout = max(float(seconds), 1.0)


def login(api_key: str | None = None, base_url: str | None = None, timeout: float | None = None) -> None:
	"""
	Authenticates the session with an API key and optional server base URL.
	"""
	if api_key:
		set_api_key(api_key)
	if base_url:
		set_base_url(base_url)
	if timeout:
		set_timeout(timeout)

"""
Unit tests for root main.py module
"""


def test_root_main_imports_app():
	"""Test that root main.py successfully imports app from app.main"""
	import main

	# Verify that app is imported
	assert hasattr(main, "app")

	# Verify that app is a FastAPI instance
	from fastapi import FastAPI

	assert isinstance(main.app, FastAPI)

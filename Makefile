.PHONY: init test ship freeze



init:
	pip install pipenv
	pipenv install --dev --pre


freeze:
	pipenv lock --pre --dev
	pipenv-setup sync --dev


ship:
	pipenv run python setup.py sdist bdist_wheel
	pipenv run twine upload dist/* --skip-existing


test:
	# pipenv run pytest tests
	pytest --cov pgark --cov-report term-missing

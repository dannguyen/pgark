.PHONY: init test ship freeze



init:
	pip install pipenv
	pipenv install --dev --pre

ship:
	pipenv run python setup.py sdist bdist_wheel
	pipenv run twine upload dist/* --skip-existing


freeze:
	pipenv lock --pre --dev
	pipenv-setup sync --dev




test:
	pipenv run pytest tests

# test:
# 	coverage run test.py
# 	coverage report -m

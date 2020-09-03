.PHONY: freeze ship test


ship:
	pipenv run python setup.py sdist bdist_wheel
	pipenv run twine upload dist/* --skip-existing


test:
	pytest

# freeze:
# 	pipenv lock --dev -r > .github/workflows/requirements.txt

# test:
# 	coverage run test.py
# 	coverage report -m

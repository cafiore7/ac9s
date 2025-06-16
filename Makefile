run:
	source venv/bin/activate && python -m ac9s.app

install:
	pip install .

test:
	pytest

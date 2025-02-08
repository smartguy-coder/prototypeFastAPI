# build-win and build-unix use only for first creation!!!
.PHONY: build-win
build-win:
	python.exe -m pip install --upgrade pip
	pip install poetry
	poetry config --local virtualenvs.in-project true
	poetry init -n
	poetry install
	echo "run >> .venv\Scripts\activate"


.PHONY: build-unix
build-unix:
	python3 -m pip install --upgrade pip
	pip3 install poetry
	poetry config --local virtualenvs.in-project true
	poetry init -n
	poetry install
	echo "run >> source .venv\bin\activate"


# add package for project requirements
.PHONY: install
install: # make install package='redis[hiredis]'
	poetry add ${package}
	poetry install --no-root

# add package for project development
.PHONY: install-dev
install-dev:  # make install-dev package='pytest'
	poetry add ${package} --group dev
	poetry install --no-root


.PHONY: run
run:
	echo 'you can switch --log-level between debug, info, warning, error, critical'
	uvicorn main:app --reload --host 127.0.0.1 --port 9000 --log-level info

.PHONY: checks
checks:
	@echo "Start check🐿"
	black .
	isort .
	flake8 .

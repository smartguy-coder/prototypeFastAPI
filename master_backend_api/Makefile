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

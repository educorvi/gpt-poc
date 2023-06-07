.PHONY: python_dist install all uninstall

all: python_dist files.txt

python_dist: setup.py gpt-poc-backend backend.py customElasticSearchRetriever.py tools.py
	python3 setup.py bdist --format=gztar

install:
	python3 setup.py install

files.txt: setup.py gpt-poc-backend backend.py customElasticSearchRetriever.py tools.py
	python3 setup.py install --record files.txt

uninstall: files.txt
	xargs rm -rf < files.txt
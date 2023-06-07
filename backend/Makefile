.PHONY: python_dist deb install all uninstall

all: python_dist files.txt

deb: setup.py gpt-poc-backend backend.py customElasticSearchRetriever.py tools.py
	python3 setup.py --command-packages=stdeb.command bdist_deb

python_dist: setup.py gpt-poc-backend backend.py customElasticSearchRetriever.py tools.py
	python3 setup.py sdist

install:
	python3 setup.py install

files.txt: setup.py gpt-poc-backend backend.py customElasticSearchRetriever.py tools.py
	python3 setup.py install --record files.txt

uninstall: files.txt
	xargs rm -rf < files.txt
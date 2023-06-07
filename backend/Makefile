.PHONY: python_dist install all uninstall

all: python_dist files.txt

deb_dist/gpt-poc-backend-%.deb: dist/gpt-poc-backend-%.tar.gz
	py2dsc-deb --with-dh-virtualenv $<

python_dist: setup.py gpt-poc-backend backend.py customElasticSearchRetriever.py tools.py
	python3 setup.py sdist

install:
	python3 setup.py install

files.txt: setup.py gpt-poc-backend backend.py customElasticSearchRetriever.py tools.py
	python3 setup.py install --record files.txt

uninstall: files.txt
	xargs rm -rf < files.txt
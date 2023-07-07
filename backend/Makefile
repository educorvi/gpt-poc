files = $(wildcard *.py) gpt-poc-backend conf.template.yaml requirements.txt
sdist_comm = sdist_dsc --suite $(shell . /etc/lsb-release && echo $$DISTRIB_CODENAME) --build-depends "dh-python" --copyright-file copyright

.PHONY: python_dist deb install all uninstall clean sign publish

all: python_dist files.txt

deb: $(files) clean
	python3 setup.py --command-packages=stdeb.command $(sdist_comm) bdist_deb

python_dist: $(files)
	python3 setup.py sdist

deb_source_package: $(files) clean
	python3 setup.py --command-packages=stdeb.command $(sdist_comm)

sign: deb_source_package
	debsign -k"727D 829C 534B E446 4F64  A8D6 CFB4 D91B 3B61 F24C" $(wildcard deb_dist/*.changes)

publish: sign
	dput -c dput.cfg educorvi-experimental $(wildcard deb_dist/*.changes)

install:
	python3 setup.py install

files.txt: $(files)
	python3 setup.py install --record files.txt

uninstall: files.txt
	xargs rm -rf < files.txt

clean:
	rm -rf dist deb_dist build gpt_poc_backend.egg-info gpt-poc-backend-*.tar.gz

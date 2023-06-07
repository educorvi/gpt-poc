FROM ubuntu:jammy
RUN apt-get update && apt-get install -y dh-virtualenv devscripts vim debhelper libgfortran5 libquadmath0 gnupg2 python3-all dh-python
RUN pip install pip-tools stdeb setuptools
ENV EDITOR=vim

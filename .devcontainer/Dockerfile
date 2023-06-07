FROM ubuntu:jammy
RUN apt-get update && apt-get install -y dh-virtualenv devscripts vim debhelper libgfortran5 libquadmath0 gnupg2
RUN pip install pip-tools
ENV EDITOR=vim

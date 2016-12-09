FROM python:latest
MAINTAINER Matthew Hartley <Matthew.Hartley@jic.ac.uk>

COPY dtool-0.2.0-py3-none-any.whl /root/
RUN pip install /root/dtool-0.2.0-py3-none-any.whl

ENTRYPOINT arctool

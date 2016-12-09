FROM python:slim
MAINTAINER Matthew Hartley <Matthew.Hartley@jic.ac.uk>

RUN apt-get update && apt-get install pigz && apt-get clean
COPY dtool-0.2.0-py3-none-any.whl /root/
RUN pip install /root/dtool-0.2.0-py3-none-any.whl

CMD ["arctool"]

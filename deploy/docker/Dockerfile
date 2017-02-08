FROM python:slim
LABEL maintainer "Matthew.Hartley@jic.ac.uk"

RUN apt-get update && apt-get install pigz libmagic1 && apt-get clean
COPY dtool-0.2.0-py3-none-any.whl /root/
RUN pip install /root/dtool-0.2.0-py3-none-any.whl

CMD ["dtool"]

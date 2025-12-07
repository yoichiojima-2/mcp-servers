FROM python:3.12

RUN apt update && apt install -y make
RUN pip install --upgrade pip && pip install uv

COPY . /pptx
WORKDIR /pptx
RUN make install

CMD ["make", "serve"]

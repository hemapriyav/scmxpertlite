FROM python:3.10

WORKDIR /consumer

COPY requirement.txt ./

RUN pip install --no-cache-dir -r requirement.txt

COPY . .

CMD ["python", "consumer.py"]
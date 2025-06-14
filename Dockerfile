FROM python:3.12-slim

RUN useradd -m servo
WORKDIR /workspace
RUN chown servo:servo /workspace

COPY servo/ /app/servo/
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

USER servo
WORKDIR /workspace

ENTRYPOINT ["python", "/app/servo/main.py"]

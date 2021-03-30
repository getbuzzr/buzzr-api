FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

ENV AWS_DEFAULT_REGION=us-east-1
ENV MODULE_NAME=main
COPY requirements.txt ./
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
COPY ./app /app

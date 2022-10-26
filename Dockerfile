FROM python:3.8-slim
WORKDIR /pythonProject


COPY requirements.txt ./

RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .

CMD ["gunicorn", "main:app", "-c", "./gunicorn.conf.py"]

#docker build --platform linux/amd64 -t godqqq/mixed-slim:3.4 .
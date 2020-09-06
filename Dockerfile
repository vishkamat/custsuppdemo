FROM python:2.7
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . ./
EXPOSE 5001
ENTRYPOINT [ "/bin/bash", "-c", "python CSS_legacy.py config.json"]

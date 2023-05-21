FROM python:3.7
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
EXPOSE 80
COPY . /app
CMD streamlit run --server.port 80 --server.enableXsrfProtection=false --server.enableCORS=false combatiq_demo.py
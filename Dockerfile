FROM python:3.10-slim

# Install Chrome and Chromedriver
RUN apt-get update && apt-get install -y wget gnupg unzip curl     && wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb     && apt-get install -y ./google-chrome-stable_current_amd64.deb     && rm google-chrome-stable_current_amd64.deb     && CHROME_VERSION=$(google-chrome --version | awk '{print $3}')     && CHROMEDRIVER_VERSION=$(echo $CHROME_VERSION | cut -d. -f1)     && wget -q "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION.0.0/chromedriver_linux64.zip"     && unzip chromedriver_linux64.zip -d /usr/local/bin/     && rm chromedriver_linux64.zip     && apt-get clean

ENV DISPLAY=:99

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

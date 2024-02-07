# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app


# Install Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] https://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable

# Install Chrome WebDriver
RUN wget -q https://chromedriver.storage.googleapis.com/LATEST_RELEASE -O /tmp/chromedriver_version && \
    wget -q https://chromedriver.storage.googleapis.com/$(cat /tmp/chromedriver_version)/chromedriver_linux64.zip -O /tmp/chromedriver.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin && \
    rm /tmp/chromedriver.zip && \
    chmod +x /usr/local/bin/chromedriver
    
# upgrade pip before install all requirements
RUN pip install --upgrade pip
# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV DJANGO_SETTINGS_MODULE=Scraper_Project.settings

# Run app.py when the container launches
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
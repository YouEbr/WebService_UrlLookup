# Defining Base Image
FROM python:3.8

# Setting working directory inside the container
WORKDIR /urllookup

# Clone everything from github!
#RUN set -x && git clone https://github.com/YouEbr/WebService_UrlLookup.git /urllookup

# Alternative to git clone: for when all the files have already been checked out before running docker build
# Copy the files
COPY *.py page.html requirements.txt ./
ADD Utility ./Utility
ADD Config ./Config

# Installing required packages
RUN set -x && pip3 install -r requirements.txt

# Run the application/ web service
CMD [ "python", "./run.py" ]
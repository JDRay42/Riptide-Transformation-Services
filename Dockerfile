# Use an official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8019 available to the world outside this container (based on your .env file)
EXPOSE 8019

# Define environment variable (if needed, you can add more)
ENV API_VERSION=v1

# Run launch.sh when the container launches
CMD ["/app/launch.sh"]

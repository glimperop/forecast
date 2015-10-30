FROM resin/rpi-raspbian:jessie
# Install Python.
RUN apt-get update \
	&& apt-get install -y python \
	# Remove package lists to free up space
	&& rm -rf /var/lib/apt/lists/*

# copy current directory into /app
COPY . /App

# run python script when container lands on device
CMD ["python", "/App/forecast-io.py"]
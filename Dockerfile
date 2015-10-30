FROM resin/rpi-raspbian:jessie
# Install Python 
RUN apt-get update \
	&& apt-get install -y git \
	&& apt-get install -y python \
	&& rm -rf /var/lib/apt/lists/*

RUN cd /home/pi/
RUN git clone http://git.eclipse.org/gitroot/paho/org.eclipse.paho.mqtt.python.git
RUN cd /home/pi/org.eclipse.paho.mqtt.python
RUN python setup.py install 


# copy current directory into /app
COPY . /App

# run python script when container lands on device
CMD ["python", "/App/forecast-io.py"]
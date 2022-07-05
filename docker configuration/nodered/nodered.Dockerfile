FROM nodered/node-red
WORKDIR /usr/src/node-red
RUN npm install node-red-contrib-tplink
RUN npm install node-red-contrib-discord
RUN npm install node-red-contrib-influxdb
RUN npm install node-red-dashboard
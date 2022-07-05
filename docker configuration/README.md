# Details
Change all <PASSWORD> into your preferred password that will be used inside docker-compose yml.
Change all <USERNAME> into your preferred username that will be used inside docker-compose yml.

# Setup
This is a docker-compose setup.
As such you need docker-compose and then run docker-compose up -d to start the containers.

Mosquitto also has persistence enabled.

# Passwords.
You must run `docker-compose run mosquitto mosquitto_passwd -U /mosquitto/config/password.txt` to encrypt the password for the mosquitto container.

In addition if you want Node-RED secured follow [securing Node-RED](https://nodered.org/docs/user-guide/runtime/securing-node-red) under section Editor & Admin API security.

The settings.js file is used to configure the Node-RED editor and loaded from nodered/settings.js in the directory.
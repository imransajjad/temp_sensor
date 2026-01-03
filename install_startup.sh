#!/bin/bash

sudo cp temp-sensor.service.example /etc/systemd/system/temp-sensor.service
sudo systemctl stop temp-sensor
sudo systemctl start temp-sensor
sudo systemctl enable temp-sensor
sudo systemctl status temp-sensor


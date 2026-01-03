#!/bin/bash

sudo systemctl stop temp-sensor
sudo systemctl disable temp-sensor
sudo systemctl status temp-sensor

rm -f /etc/systemd/system/temp-sensor.service


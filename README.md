# Temperature Sensor Project

## Introduction

My project to measure temperature and record it in a Google Drive spreadsheet.

Run this on a Raspberry Pi (or other system) with the DS18B20 Digital Temperature Sensor and record the temperature on a Google Drive Spreadsheet.

## Requirements

1. Google account with Google Drive.
2. python 3.10.11 or greater.
3. Working DS18B20 Temperature Sensor Setup [Guide](https://raspberrypi-guide.github.io/electronics/temperature-monitoring).
4. Wifi connection

## Setup

1. On your system with the temperature sensor, clone this repo.
2. In the project directory, make a `config` directory
3. (If not already provided) add the `service-account.json` file in the config directory. This file should be downloadable from the Google IAM & Admin, Service Accounts page if you generate a new key.
3. Create a copy of this [spreadsheet template](https://docs.google.com/spreadsheets/d/1H4HRqkf3VL08AwR81g5vAZK_zrVvHHmFs8ZXFuZmpcU/edit?usp=sharing) on your Google Drive. Then note down the spreadsheet ID found in the URL of your copy. For instance, the ID of the template above is `1H4HRqkf3VL08AwR81g5vAZK_zrVvHHmFs8ZXFuZmpcU`.
4. Share the spreadsheet. Add the account `temp-sensor-app@my-temp-sensor-project.iam.gserviceaccount.com` to the list of collaborators. Make sure it has editor access.

5. Create a file `config/spreadsheet-id` in the project directory
The 'spreadsheet-id' file should contain the spreadsheet ID of your spreadsheet.

6. (Optional) Do a test of the wifi connection and Google Drive access. Run the following command to post a temperature to the top row and return `python3 main.py -d"-130,-130"`.

6. Set up the service on linux to start upon startup. Copy the `temp-sensor.service.example` file into `/etc/systemd/system/temp-sensor.service`

7. Edit the absolute paths in the `/etc/systemd/system/temp-sensor.service` file to match your desired python installation and where you cloned the repo for `main.py`.

8. Enable the service and then start the service. Then you can restart the raspberry pi and this service will launch on startup. This is a good [guide](https://medium.com/@benmorel/creating-a-linux-service-with-systemd-611b5c8b91d6).

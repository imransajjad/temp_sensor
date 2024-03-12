#!/usr/bin/env python

import os
import sys
import glob
import time
import datetime
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from oauth2client.service_account import ServiceAccountCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# the file containing credentials for the service account
SERVICE_ACCOUNT_KEY_FILE = "service-account.json"

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1zru-4paYdyKorQwVoArXKOVFDSwKcgS6Ws3v2ydeRbQ"
RANGE_ENDS = ["B","C","D","E","F"]

# time format identifier
TIME_FORMAT = "%Y/%m/%d %I:%M:%S %p "

# SETTINGS
SETTINGS = {
    "UNITS": "C",
    "ALERT_TEMPS": [],
    "NORMAL_INTERVAL": 600,
    "ALERT_INTERVAL": 60,
    "ALERT_EMAILS": "",
    "ALERT_MODE": False
}

def get_credential():
    """Creates a Credential object with the correct OAuth2 authorization.

    Uses the service account key stored in SERVICE_ACCOUNT_KEY_FILE.

    Returns:
    Credentials, the user's credential.
    """
    credential = ServiceAccountCredentials.from_json_keyfile_name(
    SERVICE_ACCOUNT_KEY_FILE, SCOPES)

    if not credential or credential.invalid:
        print('Unable to authenticate using service account key.')
        sys.exit()
    return credential

def read_time_temp(devices, decimals = 1):
    """Reads the temperature from a 1-wire device"""
    data_strs = []
    for device in devices:
        with open(device, "r") as f:
            lines = f.readlines()
        while lines[0].strip()[-3:] != "YES":
            return None, None
        equals_pos = lines[1].find("t=")
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp = round(float(temp_string) / 1000.0, decimals)
            data_strs.append(temp)
    return data_strs

def upload_legend(devices):
    LEGEND_RANGE = "Sheet1!A49:" + RANGE_ENDS[len(devices)]
    try:
        service = build("sheets", "v4", credentials=get_credential())
        sheet = service.spreadsheets()

        result = (sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=LEGEND_RANGE, valueRenderOption="UNFORMATTED_VALUE").execute())
        legend_row = result.get("values", [])[0]

        resetted_device_names = [ d if lname=="reset" else lname for d,lname in zip(devices,legend_row[2:])]
        legend_row = legend_row[0:2] + resetted_device_names

        new_values = {"range":LEGEND_RANGE, "values": [legend_row]}
        print(legend_row)
        result = (sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=LEGEND_RANGE, valueInputOption='RAW', body=new_values).execute())
    except HttpError as err:
            print(err)

def upload_time_temp(timepoint, data_pts):
    FULL_RANGE = f"Sheet1!A32:" + RANGE_ENDS[len(data_pts)]
    SAMPLE_RANGE = f"Sheet1!A50:" + RANGE_ENDS[len(data_pts)]
    try:
        service = build("sheets", "v4", credentials=get_credential())

        sheet = service.spreadsheets()
        result = (sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=FULL_RANGE, valueRenderOption="UNFORMATTED_VALUE").execute())

        values = result.get("values", [])
        if not values:
            return
        
        if values[0][0] == "Settings:":
            adjust_settings(values[1:16])
        check_for_alert_mode(data_pts)

        sample_values = values[18:]

        time_zone = timepoint.astimezone().tzname()
        if len(time_zone) > 3:
            time_zone = "".join([ word[0] for word in time_zone.split(" ")])
        time_str = timepoint.strftime(TIME_FORMAT) + time_zone
        time_raw = round(timepoint.timestamp())

        new_values = {"range": SAMPLE_RANGE, "values": [ [time_raw] + [time_str] + data_pts ] + sample_values[:-1] }
        result = (sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE, valueInputOption='RAW', body=new_values).execute())

        
    except HttpError as err:
        print(err)

def get_temp_devices():
    """gets the 1-wire devices"""
    devices = [i+ "/w1_slave" for i in glob.glob("/sys/bus/w1/devices/" + "28*")]
    return sorted(devices)

def adjust_settings(values):
    global SETTINGS
    for row in values:
        if len(row) == 2:
            key, val = row[0], row[1]
            if key == "ALERT_EMAILS":
                SETTINGS["ALERT_EMAILS"] = val.split(",")
            elif key in SETTINGS.keys():
                SETTINGS[key] = val
        elif len(row) > 2:
            if row[0] == "ALERT_TEMPS":
                SETTINGS["ALERT_TEMPS"] = row[2:]

def check_for_alert_mode(data):
    global SETTINGS
    if SETTINGS["UNITS"] == "F":
        alert_temps = [5/9*(f-32) for f in SETTINGS["ALERT_TEMPS"]]
    else:
        alert_temps = SETTINGS["ALERT_TEMPS"]
    set_alert = any([i > alert_temp for i, alert_temp in zip(data,alert_temps) ])
    if (not SETTINGS["ALERT_MODE"] and set_alert):
        print("Setting Alert Mode")
    elif (SETTINGS["ALERT_MODE"] and not set_alert):
        print("Setting Normal Mode")
    SETTINGS["ALERT_MODE"] = set_alert


if __name__ == "__main__":


    devices = get_temp_devices()
    upload_legend(devices)
    while True:
        try:
            timepoint = datetime.datetime.now()
            D = read_time_temp(devices, decimals=1)
            
            upload_time_temp(timepoint, D)

            timepassed = (datetime.datetime.now() - timepoint).total_seconds()
            if SETTINGS["ALERT_MODE"]:
                time.sleep(max(0,SETTINGS["ALERT_INTERVAL"]-timepassed))
            else:
                time.sleep(max(0,SETTINGS["NORMAL_INTERVAL"]-timepassed))
            
            
        except KeyboardInterrupt:
            break

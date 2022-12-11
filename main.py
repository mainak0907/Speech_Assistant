from __future__ import print_function
import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os
import time
import pyttsx3
import webbrowser
import pytz 
import subprocess
from requests import get
import speech_recognition as sr

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
MONTHS = ["january", "february", "march", "april", "may", "june","july", "august", "september","october","november", "december"]
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_EXTENSION = ["rd", "th", "st", "nd"]

def speak(text):
    engine=pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
def get_audio():
    r=sr.Recognizer()
    with sr.Microphone() as source:
        audio=r.listen(source)
        said=""
        try:
            said=r.recognize_google(audio)
            print(said)
        except Exception as e:
            print("Exception is"+str(e))
    return said.lower()
def lastWord(string):
    lis = list(string.split(" "))
    length = len(lis)
    return lis[length-1]
"""last=lastWord(text)
if "hello" in text:
    speak("Hello, how are you?")
elif "what is your name" in text:
    speak("My name is Robby")
elif "say hi to" in text:
    speak("hello"+last+"Nice to meet you")"""
def authenticate_google():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)

    return service
#speak("Hello Mainak How are you?")
def get_events(day, service):
    # Call the Calendar API
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc=pytz.UTC
    date = date.astimezone(utc)
    end = end.astimezone(utc)
    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(),
                                        timeMax=end.isoformat(), singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak('No upcoming events found.')
    else:
        speak(f"You have {len(events)} events on this day")
        for event in events:
           start = event['start'].get('dateTime', event['start'].get('date'))
           print(start, event['summary'])
           start_time = str(start.split("T")[1].split("+")[0])
           if int(start_time.split(":")[0]) < 12:
                start_time = start_time + "am"
           else:
                start_time = str(int(start_time.split(":")[0]))+ str(int(start_time.split(":")[1]))
                start_time = start_time + "pm"

           speak(event["summary"] + " at " + start_time)


#get_events(2, service)
def get_date(text):
    text=text
    today=datetime.date.today()
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)

    if text.count("today") > 0:
        return today
    day=-1
    day_of_week=-1
    month=-1
    year=today.year
    if text.count("tomorrow") > 0:
        return tomorrow #returns tomorrows date

    for word in text.split():
        if word in MONTHS:
            month=MONTHS.index(word)+1
        elif word in DAYS:
            day_of_week=DAYS.index(word)
        elif word.isdigit():
            day=int(word)
        else:
            for ext in DAY_EXTENSION:
                found=word.find(ext)
                if found > 0:
                    try:
                        day=int(word[:found])
                    except:
                        pass
    if month < today.month and month !=-1 :
         year=year+1 # if the month mentioned is less than the current month then set it to the next year
    if month==-1 and day!=-1: # if we dont find a month but we have a day
             if day < today.day:
                 month=today.month +1
             else:
                 month=today.month
    if month==-1 and day==-1 and day_of_week !=-1: #if we only have a day of the week 
             current_day_of_week=today.weekday()
             diff = day_of_week - current_day_of_week

             if diff < 0:
                 diff+=7
                 if text.count("next") >=1:
                        dif+=7
             return today+datetime.timedelta(diff)
    if month==-1 and day==-1:
        return None
    if day!=-1:
          return datetime.date(month=month,day=day,year=year)

def note(text):
    date=datetime.datetime.now()
    file_name=str(date).replace(":","-") + "-note.txt"
    with open(file_name,"w") as f:
        f.write(text)
    subprocess.Popen(["notepad.exe",file_name])
#text=get_audio()
#print(get_date(text))
WAKE = "hello robot"
service = authenticate_google()
print("start") #to make sure that The API is working perfectly 
while True:
    print("Listening")
    text=get_audio().lower()
    if text=="goodbye":
         speak("Good bye !! thanks for talking to me")
         exit()
    if text.count(WAKE) > 0:
        speak("I am ready")
        text=get_audio()
        CALENDAR_STRS = ["what do i have", "do i have plans", "am i busy"," schedule"]
        for phrase in CALENDAR_STRS:
         if phrase in text:
           date = get_date(text)
           if date:
             get_events(date, service)
           else:
             speak("Please Try Again with date")
                  
        NOTE_STRINGS=["take note","write down"]
        for phrase in NOTE_STRINGS:
          if phrase in text:
            speak("What would you like me to write down? ")
            write_down = get_audio()
            note(write_down)
            speak("I've made a note of that.")
        BROWSER=["open google","open linkedin","open spotify"]
        if BROWSER[0] in text:
             speak("Opening google")
             webbrowser.open('http://www.google.com')
        if BROWSER[1] in text:
             speak("Opening Linkedin")
             webbrowser.open('http://www.linkedin.com')
        if BROWSER[2] in text:
             speak("Opening Spotify")
             webbrowser.open('http://www.spotify.com')

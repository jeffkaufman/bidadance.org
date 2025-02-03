#!/usr/bin/env python3

import re
import ast
import json
import pytz
import uuid
from datetime import datetime, timedelta
from icalendar import Calendar, Event

dances_json = []
with open("dances.js") as inf:
  in_json = False
  for line in inf:
    line = line.strip()
    if line.startswith("//"):
      continue

    if not in_json and line == "e = [":
      in_json = True
      dances_json.append("[")
    elif line.strip() == "];":
      dances_json.append("]")
      break
    elif in_json:
      dances_json.append(line)

def parse_js_like_object(text):
  text = re.sub(r'(\n\s*|\{\s*)(\w+):', r'\1"\2":', text)
  text = re.sub(r'\s*\+\s*', '', text)  # Remove string concatenation

  text = text.replace(' true,', ' True,').replace(' false,', ' False,')

  try:
    return ast.literal_eval(text)
  except ValueError as e:
    lines = text.split('\n')
    line_num = int(str(e).split('line')[1].split(':')[0])
    print(f"\nProblematic line {line_num}:")
    print(lines[line_num-1])
    raise

def parse_time(time_array):
    """Convert time array [hour, minute, period] to 24hr tuple"""
    hour, minute, period = time_array
    if period.lower() == 'pm' and hour != 12:
        hour += 12
    elif period.lower() == 'am' and hour == 12:
        hour = 0
    return (hour, minute)


dances = parse_js_like_object("\n".join(dances_json))

def to_ical(events):
    # Create calendar
    cal = Calendar()
    cal.add('prodid', '-//BIDA Events//bidadance.org//')
    cal.add('version', '2.0')
    eastern = pytz.timezone('America/New_York')
    
    for event in events:
        title = event.get("title", "Contra Dance")
        e = Event()

        if "end_date" not in event:
          # Set start time (default 7pm unless specified)
          if 'lesson_start' in event:
            start_hour, start_minute = parse_time(event['lesson_start'])
          else:
            start_hour, start_minute = 19, 0  # 7pm
            
          # Create datetime objects
          start_dt = eastern.localize(
            datetime(*event["date"], start_hour, start_minute))
          end_dt = start_dt + timedelta(hours=3, minutes=30)  # 3.5 hours duration
        else:
          start_dt = eastern.localize(datetime(*event["date"], 0, 0))
          end_dt = eastern.localize(datetime(*event["end_date"], 23, 59))

        # Add event details
        e.add('summary', title)
        e.add('dtstart', start_dt)
        e.add('dtend', end_dt)
        e.add('dtstamp', datetime.now())
        
        unique_string = f"{title}-{'-'.join(str(x) for x in event['date'])}"
        e.add('uid', str(uuid.uuid5(uuid.NAMESPACE_DNS, unique_string)))
        
        if 'link' in event:
            e.add('url', event['link'])
            
        # Add event to calendar
        cal.add_component(e)
    
    return cal.to_ical()

ical = to_ical(parse_js_like_object("\n".join(dances_json)))
with open("events.ics", "wb") as outf:
  outf.write(ical)

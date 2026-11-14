#!/usr/bin/env python3

# Run by cron via:
#
#   # m h  dom mon dow   command
#   13 * * * * /home/jefftk/code/bidadance.org/refresh-ical.sh


import os
import re
import html
import sys
import pytz
import uuid
import shutil
import filecmp
import textwrap
from datetime import datetime, timedelta
from icalendar import Calendar, Event

dances_fname = "dances.js"
last_dances_fname = "last_dances.js"
if os.path.exists(last_dances_fname):
  if filecmp.cmp(last_dances_fname, dances_fname):
    exit(0) # no changes since last run

class DancesParser:
  """Reads the list of dances out of dances.js.

  Handles the subset of JavaScript that dances.js uses: objects, arrays,
  strings of all three kinds, true/false, and // comments.
  """

  SPACE = re.compile(r"(?:\s+|//[^\n]*)*")
  STRING = re.compile(r"""(["'`])((?:\\.|(?!\1).)*)\1""", re.DOTALL)
  FIELD_NAME = re.compile(r"(\w+)\s*:")

  def __init__(self, text):
    self.text = text
    self.pos = text.index("e = [") + len("e = ")

  def error(self, message):
    line = self.text.count("\n", 0, self.pos) + 1
    return ValueError(f"dances.js line {line}: {message}")

  def peek(self):
    self.pos = self.SPACE.match(self.text, self.pos).end()
    return self.text[self.pos]

  def parse_value(self):
    char = self.peek()
    if char == "{":
      fields = self.parse_items("}", self.parse_field)
      if len(dict(fields)) < len(fields):
        print(self.error("a field is set twice"), file=sys.stderr)
      return dict(fields)
    if char == "[":
      return self.parse_items("]", self.parse_value)
    for word, value in (("true", True), ("false", False)):
      if self.text.startswith(word, self.pos):
        self.pos += len(word)
        return value
    match = self.STRING.match(self.text, self.pos)
    if not match:
      raise self.error(f"unexpected {char!r}")
    self.pos = match.end()
    return re.sub(r"\\(.)", r"\1", match.group(2), flags=re.DOTALL)

  def parse_field(self):
    match = self.FIELD_NAME.match(self.text, self.pos)
    if not match:
      raise self.error("expected a field name")
    self.pos = match.end()
    return match.group(1), self.parse_value()

  def parse_items(self, close, parse_item):
    self.pos += 1
    items = []
    while self.peek() != close:
      items.append(parse_item())
      if self.peek() == ",":
        self.pos += 1
      elif self.peek() != close:
        raise self.error(f"expected , or {close}")
    self.pos += 1
    return items


def parse_date(date):
    return [int(part) for part in date.split("-")]

def parse_time(time):
    """Convert a time like "4pm" or "7:30pm" to a 24hr tuple"""
    hour, minute, period = re.fullmatch(
      r"(\d+)(?::(\d+))?\s*(am|pm)", time.strip().lower()).groups()
    hour, minute = int(hour), int(minute or 0)
    if period == 'pm' and hour != 12:
        hour += 12
    elif period == 'am' and hour == 12:
        hour = 0
    return (hour, minute)

def is_cancelled(event):
    title = event.get("title", "").lower()
    return title.startswith("no dance") or "cancel" in title

def notes_to_text(notes):
    """Convert Markdown notes to plain text for the calendar"""
    text = textwrap.dedent(notes).strip()
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)  # links
    text = re.sub(r'\*+', '', text)  # bold and italics
    text = re.sub(r'<[^>]+>', ' ', text)  # raw HTML
    text = text.replace('\\\n', ' ')  # line breaks
    return re.sub(r'\s+', ' ', html.unescape(text)).strip()

def get_description(event):
    """Generate description from event details"""
    parts = []

    if 'schedule' in event:
        parts.append('; '.join(event['schedule']))

    if 'notes' in event:
        parts.append(notes_to_text(event['notes']))

    # Add performers info matching JS logic
    if event.get('caller') or event.get('band'):
        if not event.get('band'):
            parts.append(f"{event['caller']} calling.")
        elif not event.get('caller'):
            parts.append(f"{event['band']} playing.")
        else:
            parts.append(f"{event['caller']} calling to {event['band']}.")

    if 'masks' in event:
        parts.append(f"This dance is mask-{event['masks']}")

    return ' '.join(
        part if part[-1] in '.!?' else part + '.' for part in parts)

def make_uid(title, date):
    unique_string = f"{title}-{'-'.join(str(x) for x in date)}"
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, unique_string))

def to_ical(events):
    # Create calendar
    cal = Calendar()
    cal.add('prodid', '-//BIDA Events//bidadance.org//')
    cal.add('version', '2.0')
    eastern = pytz.timezone('America/New_York')

    def at(date, time):
        return eastern.localize(datetime(*date, *time))

    def add(title, start, end, event, uid):
        e = Event()
        e.add('summary', title)
        e.add('dtstart', start)
        e.add('dtend', end)
        e.add('dtstamp', datetime.now())
        description = get_description(event)
        if description:
            e.add('description', description)
        e.add('uid', uid)
        if 'link' in event:
            link = event['link']
            e.add('url', link if isinstance(link, str) else link[0])
        cal.add_component(e)

    for event in events:
        if is_cancelled(event):
            continue

        date = parse_date(event["date"])
        lesson = parse_time(event.get("lesson_start", "7pm"))
        default_title = ("Afternoon Contra Dance" if lesson <= (18, 59)
                         else "Contra Dance")
        title = "BIDA " + event.get("title", default_title)
        # The UID comes from the title as the feed has always made it,
        # defaulting to "Contra Dance", so calendars update an existing
        # entry instead of adding a new one.  Changing a dance's title
        # gives it a new UID.
        uid = make_uid("BIDA " + event.get("title", "Contra Dance"), date)

        if "end_date" in event:
            add(title, at(date, (0, 0)),
                at(parse_date(event["end_date"]), (23, 59)), event, uid=uid)
            continue

        if "start" in event:
            # Something other than a contra dance, like a workshop.
            start_dt = at(date, parse_time(event["start"]))
            end_dt = (at(date, parse_time(event["end"])) if "end" in event
                      else start_dt + timedelta(hours=1))
            add(title, start_dt, end_dt, event, uid=uid)
            continue

        if event.get("hide_times") and "schedule" not in event:
            # Not a regular dance: use the times only if both are given.
            start = event.get("dance_start") or event.get("lesson_start")
            if start and "dance_end" in event:
                add(title, at(date, parse_time(start)),
                    at(date, parse_time(event["dance_end"])), event, uid=uid)
            else:
                day = datetime(*date).date()
                add(title, day, day + timedelta(days=1), event, uid=uid)
            continue

        # One calendar entry per dance: anything that should be its own
        # entry, like a workshop, is its own dance in dances.js.
        if "lesson_start" in event or "dance_start" not in event:
            start_dt = at(date, lesson)
            end_dt = (at(date, parse_time(event["dance_end"]))
                      if "dance_end" in event
                      else start_dt + timedelta(hours=3, minutes=30))
        else:
            start_dt = at(date, parse_time(event["dance_start"]))
            end_dt = (at(date, parse_time(event["dance_end"]))
                      if "dance_end" in event
                      else start_dt + timedelta(hours=3))

        add(title, start_dt, end_dt, event, uid=uid)

    return cal.to_ical()

with open(dances_fname) as inf:
  dances = DancesParser(inf.read()).parse_value()

ical = to_ical(dances)
with open("events.ics", "wb") as outf:
  outf.write(ical)

shutil.copyfile(dances_fname, last_dances_fname)

#!/usr/bin/env python3
import csv
import time
import datetime

cpi = {} # year, month -> index
with open("CPIAUCSL.csv") as inf:
  for date, cpiaucsl in csv.reader(inf):
    if date == "DATE":
      continue
    y, m, d = date.split("-")
    cpi[int(y), int(m)] = float(cpiaucsl)

def current_dollars(year, month, amount):
  if amount is None:
    return amount

  now_y_m = max(cpi)
  if (year, month) > now_y_m:
    return amount

  now_index = cpi[now_y_m]
  then_index = cpi[year, month]
  return round(amount * now_index / then_index)

if max(cpi)[0] < (datetime.date.today() - datetime.timedelta(days=60)).year:
  print("Inflation numbers are a bit old; no data since %s-%s" % (max(cpi)))
  print("Download new CSV from https://fred.stlouisfed.org/series/CPIAUCSL")
  exit(1)

print("Visit https://docs.google.com/spreadsheets/d/1PvCEAlAluF5Cf0J2s_C0AaAQ4HpgjF4WT1XVpV5DcuQ/edit#gid=1315149313")
print("and make sure it's up to date.  Then paste contents here.")
print("Press Ctrl-C when done.")

lines = []
try:
  while True:
    lines.append(input())
except KeyboardInterrupt:
  pass

def parse_money(s):
  s = s.replace('$', '').replace(',', '').strip()
  if not s:
    return None

  return round(float(s))

def to_epoch(year, month, day):
  try:
    return int(time.mktime(time.strptime('%s-%s-%s' % (
      year, month, day), '%Y-%m-%d')))
  except Exception:
    print((year, month, day))
    raise

vals = []
for line in lines:
  if not line.strip():
    continue
  date_s, income_s, profit_s = line.split('\t')
  if date_s == 'date':
    continue

  year, month, day = date_s.split('-')
  ts = to_epoch(year, month, day)
  income = parse_money(income_s)
  profit = parse_money(profit_s)
  vals.append((ts, income, profit,
               current_dollars(int(year), int(month), income),
               current_dollars(int(year), int(month), profit)))

import json
with open('/home/jefftk/bd/financials.log', 'w') as outf:
  outf.write(json.dumps(vals))

print('\nWrote %s data points.' % len(vals))

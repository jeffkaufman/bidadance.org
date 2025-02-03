#!/usr/bin/env bash

cd ~/bidadance.org-ical/
git pull
./make-ical.py

if [[ -n $(git status --porcelain) ]]; then
  git commit -a -m "calendar: update"
  git push
fi

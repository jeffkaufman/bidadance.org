# bidadance.org

The source for https://www.bidadance.org/

This is almost all bare html: if you want to make a change, modify the
relevant HTML file directly.

Exceptions:

* The list of upcoming dances is in JSON at the beginning of
  dances.js.  Don't delete old dances: they're only shown when someone
  chooses to display past dances, and it's nice to preserve the
  history.  After changing the list run `./make-ical.py` to update the
  calendar.
  * But if you forget to run `make-ical.py` then Jeff has a cron job
    that runs `./refresh-ical.sh` hourly, which will do it for you.
* `attendance.log` and `financials.log` are created by
  `update_attendance.py` and `update_financials.py`.

This is deployed with GitHub Pages, and changes go live when you push them.

# bidadance.org

The source for https://www.bidadance.org/

This is almost all bare html: if you want to make a change, modify the
relevant HTML file directly.

Exceptions:

* The list of dances is in dances.js, and `render-dances.js` turns it
  into the page.  See "Editing dances" below.  Don't delete old
  dances: they're only shown when someone chooses to display past
  dances, and it's nice to preserve the history.  After changing the
  list run `./make-ical.py` to update the calendar.
  * But if you forget to run `make-ical.py` then Jeff has a cron job
    that runs `./refresh-ical.sh` hourly, which will do it for you.
* `marked.js` is an unmodified copy of [marked](https://marked.js.org/)
  v18.1.0, which turns Markdown into HTML.
* `attendance.log` and `financials.log` are created by
  `update_attendance.py` and `update_financials.py`.

This is deployed with GitHub Pages, and changes go live when you push them.
To preview a change, open `index.html` in your browser.

## Editing dances

Each dance in dances.js looks like this.  Copying a nearby dance is a
good way to start, and every field except `date` is optional:

```js
{
  date: "2026-11-22",
  title: "Afternoon Family Dance + Contra Dance",
  caller: "Qwill Duvall",
  band: "Supertrad",
  masks: "optional",
  lesson_start: "4pm",
  schedule: [
    "2:15 Doors open",
    "2:30-3:30 Family dance (mask-optional)",
    "4:00-4:30 Beginner's Lesson (mask-required)",
    "4:30-7:30 Evening dance (mask-required)",
  ],
  notes: `
    Wear a costume, or something that'll **glow in blacklights**!

    See [our accessibility page](/accessibility) for details.
  `,
  link: "https://www.facebook.com/events/670201915407915/",
},
```

* `date`: the date as year-month-day.  For a multi-day event, also set
  `end_date`.
* `title`: defaults to "Contra Dance", or "Afternoon Contra Dance" if
  the lesson starts by 6pm.  A title starting with "No dance" shows the
  dance as cancelled.
* `masks`: `"optional"` or `"required"`.  Leave it out if neither fits,
  and explain in `notes`.
* `lesson_start`, `dance_start`, `dance_end`: times like `"4pm"` or
  `"7:30pm"`.  The defaults are a 7pm lesson, then a dance from 30
  minutes after the lesson starts until three hours later.
* `schedule`: a list of lines, each a time with no spaces in it and
  then what's happening.  It shows as a table, in place of the usual
  lesson and dance times, and "mask-optional" and "mask-required" turn
  into links.
* `hide_times: true`: hides the usual lesson and dance times without a
  schedule, for events like workshops.
* `notes`: anything else, written in Markdown between backticks.  Use
  `**bold**`, `*italics*`, `[link text](https://example.com)`, and a
  blank line between paragraphs.  HTML works here too if you need it.
  If you need a literal backtick, write it as `` \` ``.
* `link`: a link for the whole event, or a list of links in square
  brackets.

Mind the punctuation: text goes in quotes and each field ends with a
comma.  If the page says it couldn't load the list of dances, look for
a missing quote or comma near your change.

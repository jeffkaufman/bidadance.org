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

Each dance in dances.js looks like this, and every field except `date`
is optional:

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
* `start`, `end`: for something that isn't a contra dance, like a
  workshop or family dance, times like `"2:30pm"`.  The page shows just
  these times under the title, with no lesson or dance times.
* `schedule`: a list of lines, each a time with no spaces in it and
  then what's happening.  It shows as a table, in place of the usual
  lesson and dance times, and "mask-optional" and "mask-required" turn
  into links.
* `hide_times: true`: hides the usual lesson and dance times without a
  schedule, for events like workshops.  The calendar feed shows these as
  all-day unless you also set `dance_start` (or `lesson_start`) and
  `dance_end`.
* Each dance is one entry in the calendar feed.  With a `schedule`, the
  entry runs from the start of the first thing in it to the end of the
  last, skipping lines without an end time like "Doors open", or from
  `lesson_start` (or `dance_start`) if you set one.  Schedule times
  without am/pm are read as pm.  Dances whose title starts with "No
  dance" or mentions "cancel" are left out of the feed.
* Something else on the same day, like a workshop, family dance, or
  other dance style before the contra dance, gets its own entry in
  dances.js, just before the dance, with its own title, `start`, and
  `end`.  The page shows a day's entries together.  The dance keeps the
  full schedule, but its title is just the dance (here the default,
  "Contra Dance"), and it sets `lesson_start` so its calendar entry
  starts with the lesson:

  ```js
  {
    date: "2026-12-20",
    title: "Family Dance",
    masks: "optional",
    start: "5:30pm",
    end: "6:30pm",
  },
  {
    date: "2026-12-20",
    lesson_start: "7pm",
    schedule: [
      "5:30-6:30 Family dance (mask-optional)",
      "6:30-7:30 Potluck (mask-optional)",
      "7:00-7:30 Beginner's Lesson (mask-required)",
      "7:30-10:30 Evening dance (mask-required)",
    ],
  },
  ```
* `notes`: anything else, written in Markdown between backticks.  Use
  `**bold**`, `*italics*`, `[link text](https://example.com)`, and a
  blank line between paragraphs.  HTML works here too if you need it.
  If you need a literal backtick, write it as `` \` ``.
* `link`: a link for the whole event, or a list of links in square
  brackets.

Mind the punctuation: text goes in quotes and each field ends with a
comma.  If the page says it couldn't load the list of dances, look for
a missing quote or comma near your change.

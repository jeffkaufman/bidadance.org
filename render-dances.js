next_event = document.getElementById("next-event");
events = document.getElementById("events");
past_events = document.getElementById("past-events");

function getHostname(url) {
  var hostname = url.split('/')[2];
  if (hostname.slice(0,4) == "www.") {
    hostname = hostname.slice(4);
  }

  if (hostname == "facebook.com") {
    return "facebook";
  } else if (hostname == "meetup.com") {
    return "meetup";
  } else if (hostname == "instagram.com") {
    return "instagram";
  } else {
    return hostname;
  }
}

function parse_date(s) {
  const [year, month, day] = s.split("-").map(Number);
  return new Date(year, month - 1, day);
}

// Turns "4pm" or "7:30pm" into [4, 0, "pm"] or [7, 30, "pm"].
function parse_time(s) {
  const [, hour, minute, amPm] = s.trim().toLowerCase().match(
    /^(\d+)(?::(\d+))?\s*(am|pm)$/);
  return [Number(hour), Number(minute || 0), amPm];
}

function format_time(t) {
  const [hour, minute, amPm] = t;
  console.log("format_time", hour, minute, amPm, (hour.toString() + (minute ? (":" + minute) : "") + amPm));
  return hour.toString() + (minute ? (":" + minute) : "") + amPm;
}

function add_time(t, delta_hour, delta_minute) {
  [old_hour, old_minute, old_amPm] = t;
  let new_amPm = old_amPm;
  let new_minute = old_minute + delta_minute;
  let extra_hour = 0;
  if (new_minute > 60) {
    extra_hour = 1;
    new_minute -= 60;
  }
  let new_hour = old_hour + delta_hour + extra_hour;
  if (new_hour > 12) {
    new_hour -= 12;
    new_amPm = (old_amPm == "am" ? "pm" : "am");
  }
  return [new_hour, new_minute, new_amPm];
}

// Multi-line notes are indented to line up with the code around them, but
// Markdown would treat that indentation as a code block.
function dedent(text) {
  const lines = text.split("\n");
  const indents = lines.filter(line => line.trim())
                       .map(line => line.match(/^ */)[0].length);
  const indent = Math.min(...indents);
  return lines.map(line => line.slice(indent)).join("\n");
}

function render_masks(masks) {
  var masks_p = document.createElement("p");
  masks_p.className = "masks";
  masks_p.innerHTML =
    "This dance is <a href=/accessibility><strong>mask-" + masks +
    "</strong></a>";
  return masks_p;
}

function render_schedule(schedule) {
  var table = document.createElement("table");
  schedule.forEach(line => {
    const [, time, activity] = line.match(/^(\S+)\s+(.*)$/);
    var row = table.insertRow();
    row.insertCell().textContent = time;
    row.insertCell().innerHTML = marked.parseInline(activity).replace(
      /mask-(required|optional)/g,
      "<a href=/accessibility><strong>$&</strong></a>");
  });
  return table;
}

function render_notes(notes) {
  var notes_div = document.createElement("div");
  notes_div.className = "notes";
  notes_div.innerHTML = marked.parse(dedent(notes));
  return notes_div;
}

function gen_events() {
  var yesterday = new Date(); yesterday.setDate(yesterday.getDate() - 1);
  var days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday",
              "Friday", "Saturday"];
  for (var i = 0; i < e.length; i++) {
    var event = e[i];

    event.date = parse_date(event.date);
    let links = null;
    if (event.link) {
      if (Array.isArray(event.link)) {
        links = event.link;
      } else {
        links = [event.link];
      }
    }
    if (links) {
      var event_a = document.createElement("a");
      event_a.href = links[0];
    }
    var event_div = document.createElement("div");
    event_div.className = "event";
    var date_div = document.createElement("div");
    date_div.className = "date";
    var date_text = days[event.date.getDay()] + " " +
                    (event.date.getMonth() + 1) + "/" +
                    event.date.getDate();
    if (event.date.getYear() != new Date().getYear()) {
      date_text += "/" + (event.date.getYear() + 1900);
    }
    date_div.textContent = date_text;

    var time_text = "";
    var lesson_text = "";

    var default_title = "Contra Dance";
    if (event.time) {
      time_text = event.time;

    } else {
      const lesson_start = event.lesson_start ?
        parse_time(event.lesson_start) : [7, 0, "pm"];

      if (lesson_start[0] <= 6) {
        date_div.classList.add("afternoon");
        default_title = "Afternoon Contra Dance";
      }

      lesson_text = "Lesson: " + format_time(lesson_start);
      const dance_start = event.dance_start ?
        parse_time(event.dance_start) : add_time(lesson_start, 0, 30);
      const dance_end = event.dance_end ?
        parse_time(event.dance_end) : add_time(dance_start, 3, 0);
      time_text = "Dance: " + format_time(dance_start) + "-" + format_time(dance_end);
    }

    var lesson_div = document.createElement("div");
    lesson_div.className = "lesson";
    lesson_div.textContent = lesson_text;

    var time_div = document.createElement("div");
    time_div.className = "time";
    time_div.textContent = time_text;

    event_div.appendChild(date_div);

    var danceIsHappening = true;
    if (event.title && event.title.toLowerCase().startsWith("no dance")) {
      danceIsHappening = false;
    }

    var details_div = document.createElement("div");
    details_div.className = "details";
    event.title = event.title || default_title;
    var title_div = document.createElement("div");
    title_div.className = "title";
    title_div.textContent = event.title;
    event_div.appendChild(title_div);

    if (danceIsHappening && !event.hide_times && !event.schedule) {
      event_div.appendChild(lesson_div);
      event_div.appendChild(time_div);
    }

    if (event.schedule || event.notes) {
      var custom_div = document.createElement("div");
      custom_div.className = "custom";
      if (event.schedule) {
        custom_div.appendChild(render_schedule(event.schedule));
      }
      if (event.notes) {
        custom_div.appendChild(render_notes(event.notes));
      }
      details_div.appendChild(custom_div);
    }
    if (event.caller || event.band) {
      var performers_div = document.createElement("div");
      performers_div.className = "performers";
      if (!event.band) {
        performers_div.textContent = event.caller + " calling."
      } else if (!event.caller) {
        performers_div.textContent = event.band + " playing."
      } else {
        performers_div.textContent = event.caller + " calling to " + event.band;
      }
      details_div.appendChild(performers_div);
    }
    if (event.masks) {
      details_div.appendChild(render_masks(event.masks));
    }
    var links_div = document.createElement("div");
    if (links) {
      links_div.appendChild(document.createTextNode(" details on "));
      let is_first = true;
      links.forEach(link => {
        if (!is_first) {
          links_div.appendChild(document.createTextNode(", "));
        }
        const link_a = document.createElement("a");
        link_a.textContent = getHostname(link);
        link_a.href = link;
        link_a.className = "marklink";
        links_div.appendChild(link_a);
        is_first = false;
      })
    } else if (event.title.toLowerCase().startsWith("no dance")) {
      links_div.textContent ="Dance cancelled.";
    } else if (!event.caller && !event.band && !event.masks &&
               !event.schedule && !event.notes) {
      links_div.textContent ="details TBA";
    } else {
      links_div.style.display = "none";
    }
    details_div.appendChild(links_div);
    event_div.appendChild(details_div);
    clear_div = document.createElement("div");
    clear_div.className = "clear";
    event_div.appendChild(clear_div);

    var event_to_append = event_div;
    if (links) {
      event_a.appendChild(event_div);
      event_to_append = event_a;
    }

    if (event.date < yesterday) {
      if (past_events.children.length == 0) {
        past_events.appendChild(event_to_append);
      } else {
        past_events.insertBefore(
          event_to_append, past_events.firstChild);
      }
    } else {
      if (next_event.children.length == 0 &&
          !event_to_append.innerHTML.toLowerCase().includes("sold out")) {
        next_event.appendChild(
            event_to_append.cloneNode(/*deep=*/true));
      }
      events.appendChild(event_to_append);
    }
  }

}

if (typeof e === "undefined") {
  // dances.js didn't run, almost always because of a typo.
  events.textContent = "Sorry, we couldn't load the list of dances.";
  events.textContent += " If you just edited dances.js, look for a typo";
  if (window.dances_error && window.dances_error.lineno) {
    events.textContent += " near line " + window.dances_error.lineno + ": " +
      window.dances_error.message;
  }
  events.textContent += ".";
} else {
  gen_events();
}

show_past = false;
toggle_past = document.getElementById("toggle-past");

function update_toggle_past() {
  if (show_past) {
    toggle_past.textContent = "Hide Past Events";
  } else {
    toggle_past.textContent = "Show Past Events";
  }
}

toggle_past.onclick = function() {
  show_past = !show_past;
  past_events.style.display = show_past ? "block" : "none";
  update_toggle_past();
  return false;
};

update_toggle_past();

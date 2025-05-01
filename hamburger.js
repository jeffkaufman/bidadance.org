const hamburger_container = document.createElement('div');
hamburger_container.innerHTML =
  '<div id="nav-wrapper">' +
  '<div id="hamburger-wrapper">' +
  '<button class="hamburger" id="menu-toggle">&#9776;</button>' +
  '<div id="nav">' +
  '<dl>' +

  '<dt>About BIDA' +
  '<dd>' +
  '<a href="https://www.bidadance.org/about">About</a>' +
  '<a href="https://www.bidadance.org/board">Board</a>' +
  '<a href="https://www.bidadance.org/board-roles">Board Roles</a>' +
  '<a href="https://www.bidadance.org/bylaws">Bylaws</a>' +
  '<a href="https://www.bidadance.org/graphs">Charts and Graphs</a>' +
  '<a href="https://www.bidadance.org/faq">FAQ</a>' +

  '<dt>Callers and Bands' +
  '<dd>' +
  '<a href="https://www.bidadance.org/band-welcome">Band Welcome</a>' +
  '<a href="https://www.bidadance.org/caller-welcome">Caller Welcome</a>' +
  '<a href="https://www.bidadance.org/get-involved">Get Involved</a>' +
  '<a href="https://www.bidadance.org/payscale">Payscale</a>' +
  '<a href="https://www.bidadance.org/open-band-tune-list">Open Band Tune List</a>' +
  '<a href="https://www.bidadance.org/open-band-leading">Open Band Leading</a>' +

  '<dt>Resources' +
  '<dd>' +
  '<a href="https://www.bidadance.org/accessibility">Accessibility</a>' +
  '<a href="https://www.beantownstomp.com">Beantown Stomp</a>' +
  '<a href="http://blog.bidadance.org/">Blog</a>' +
  '<a href="https://www.bidadance.org/join">Mailing Lists</a>' +
  '<a href="https://www.bidadance.org/safety">Safety</a>' +

  '</dl>' +
  '</div>' +
  '</div>' +
  '</div>';

document.currentScript.parentNode.insertBefore(
    hamburger_container, document.currentScript);

function startHamburger() {
  const menuToggle = document.getElementById("menu-toggle");
  const nav = document.getElementById("nav");
  menuToggle.addEventListener("click", function() {
    nav.classList.toggle("active");
  });
  document.addEventListener("click", function(event) {
    if (!nav.contains(event.target) &&
       !menuToggle.contains(event.target)) {
      nav.classList.remove("active");
    }
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", startHamburger);
} else {
  startHamburger();
}

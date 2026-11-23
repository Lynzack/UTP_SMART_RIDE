(() => {
  "use strict";

  let results = null;
  let locations = [];
  const $ = id => document.getElementById(id);

  const escapeHTML = value => String(value ?? "").replace(/[&<>"']/g, char => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[char]));

  const number = value => Number.isFinite(Number(value))
    ? Number(value).toLocaleString(undefined, { maximumFractionDigits: 2 })
    : "—";

  function showNotice(message, error = false) {
    const box = $("global-notice");
    box.textContent = message;
    box.className = "global-notice show" + (error ? " error" : "");
    window.clearTimeout(showNotice.timer);
    showNotice.timer = window.setTimeout(() => box.classList.remove("show"), 6500);
  }

  function setEngineStatus(text, connected = false) {
    $("engine-status").textContent = text;
    $("status-indicator").classList.toggle("connected", connected);
  }

  function navigate(viewId) {
    document.querySelectorAll(".view").forEach(section =>
      section.classList.toggle("active", section.id === viewId)
    );
    document.querySelectorAll(".nav").forEach(button =>
      button.classList.toggle("active", button.dataset.view === viewId)
    );
    const labels = {
      home: "Overview", find: "Find a Ride", offer: "Offer a Ride",
      matching: "Matching Results", routes: "Route Maps", locations: "Campus Locations"
    };
    $("page-name").textContent = labels[viewId] || "Overview";
    $("sidebar").classList.remove("open");
    if (viewId === "routes") renderRoutes();
    if (viewId === "matching") renderResults();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function allAssignments() {
    return Array.isArray(results?.assignments) ? results.assignments : [];
  }

  function getLocationName(value) {
    const found = locations.find(item => String(item.id) === String(value));
    return found ? found.name : value;
  }

  function normaliseLocations(data) {
    return (Array.isArray(data) ? data : []).map(item => {
      if (Array.isArray(item)) {
        return { id: item[0], name: item[1], latitude: item[2], longitude: item[3] };
      }
      return {
        id: item.locationID ?? item.id,
        name: String(item.locationName ?? item.name ?? item.locationID ?? item.id).trim(),
        latitude: item.latitude,
        longitude: item.longitude
      };
    }).filter(item => item.id != null);
  }

  function populateLocationSelects() {
    document.querySelectorAll(".location-select").forEach(select => {
      const first = select.querySelector("option")?.textContent || "Select location";
      select.innerHTML = `<option value="">${escapeHTML(first)}</option>` +
        locations.map(location =>
          `<option value="${escapeHTML(location.id)}">${escapeHTML(location.name)}</option>`
        ).join("");
    });
  }

  function renderLocationDirectory() {
    $("location-grid").innerHTML = locations.map(location => `
      <article class="location-card">
        <div class="location-card-top"><em>${escapeHTML(location.id)}</em></div>
        <strong>${escapeHTML(location.name)}</strong>
        <small>${location.latitude != null && location.longitude != null
          ? `${number(location.latitude)}, ${number(location.longitude)}`
          : "UTP campus location"}</small>
      </article>
    `).join("") || `<div class="empty-state">No locations were returned by the backend.</div>`;
  }

  function renderResults() {
    if (!results) return;

    const totalDrivers = Number(results.totalDrivers ?? allAssignments().length);
    const totalPassengers = Number(results.totalPassengers ?? 0);
    const assigned = Number(results.totalAssigned ?? 0);
    const unassigned = Number(results.totalUnassigned ?? 0);
    const percentage = totalPassengers ? Math.round(assigned / totalPassengers * 100) : 0;

    $("total-drivers").textContent = number(totalDrivers);
    $("total-passengers").textContent = number(totalPassengers);
    $("total-assigned").textContent = number(assigned);
    $("total-unassigned").textContent = number(unassigned);
    $("allocation-rate").textContent = `${percentage}% passenger allocation`;
    $("allocation-percent").innerHTML = `${percentage}<small>%</small>`;
    $("allocation-bar").style.width = `${percentage}%`;
    $("best-fitness").textContent = number(results.bestFitness);
    $("generation-count").textContent = results.generations ?? "—";
    $("result-status").textContent = "Latest backend results";
    $("result-status").classList.add("ready");

    // const unassignedIds = Array.isArray(results.unassignedPassengers)
    //   ? results.unassignedPassengers : [];
    // $("unassigned-list").innerHTML = unassignedIds.length
    //   ? unassignedIds.map(id => `<span class="unassigned-chip">${escapeHTML(id)}</span>`).join("")
    //   : `<span class="muted">All passengers in this result were assigned.</span>`;

    const unassignedAnalysis = Array.isArray(results.unassignedAnalysis)
      ? results.unassignedAnalysis : [];

    $("unassigned-list").innerHTML = unassignedAnalysis.length
      ? unassignedAnalysis.map(item => `
          <div class="unassigned-item">
            <div class="unassigned-item-header">
              <strong>${escapeHTML(item.passengerID)}</strong>
              <span class="unassigned-badge">Unassigned</span>
            </div>

            <p>${escapeHTML(item.reason)}</p>

            <small>
              Eligible drivers: ${
                item.eligibleDrivers?.length
                  ? item.eligibleDrivers.map(escapeHTML).join(", ")
                  : "None"
              }
            </small>
          </div>
        `).join("")
      : `<span class="muted">All passengers in this result were assigned.</span>`;
    renderAssignmentTable();
  }

  function renderAssignmentTable() {
    if (!results) return;
    const query = ($("assignment-search").value || "").trim().toLowerCase();
    const rows = [];

    allAssignments().forEach(driver => {
      const passengers = Array.isArray(driver.assignedPassengers) ? driver.assignedPassengers : [];
      const passengerText = passengers.map(p => p.passengerID).join(", ");
      if (!`${driver.driverID} ${passengerText}`.toLowerCase().includes(query)) return;

      const scoreText = passengers.length
        ? passengers.map(p => `<span class="score-pill">${escapeHTML(p.passengerID)} · ${number(p.compatibility)}</span>`).join(" ")
        : "—";

      rows.push(`
        <tr>
          <td><strong class="id-strong">${escapeHTML(driver.driverID)}</strong></td>
          <td>${passengers.length ? passengers.map(p => escapeHTML(p.passengerID)).join(", ") : "—"}</td>
          <td>${scoreText}</td>
          <td>${escapeHTML(driver.availableSeats ?? "—")}</td>
          <td><span class="allocation-pill ${passengers.length ? "" : "empty"}">${passengers.length ? "Matched" : "No allocation"}</span></td>
        </tr>
      `);
    });

    $("assignment-table").innerHTML = rows.join("") ||
      `<tr><td colspan="5">No matching assignment records found.</td></tr>`;
  }

  function formatStop(stop) {
    const raw = String(stop ?? "");
    const match = raw.match(/^(.*)_(PICKUP|DROPOFF)$/i);
    if (!match) return raw;
    return `${match[1]} · ${match[2].toLowerCase() === "pickup" ? "Pickup" : "Drop-off"}`;
  }

  function renderRoutes() {
    const routes = Array.isArray(results?.optimizedRoutes) ? results.optimizedRoutes : [];
    if (!results) {
      $("route-list").innerHTML = `
        <div class="empty-state"><div>⌁</div><h3>No matching results loaded</h3>
        <p>Open AI Matching to load existing results or run the algorithm.</p>
        <button class="button button-blue" data-go="matching">Go to AI Matching</button></div>`;
      return;
    }
    if (!routes.length) {
      $("route-list").innerHTML = `
        <div class="empty-state"><div>⌁</div><h3>No optimised routes in this result</h3>
        <p>The current result does not contain any drivers with assigned passengers.</p></div>`;
      return;
    }

    $("route-list").innerHTML = routes.map(route => {
      const passengers = Array.isArray(route.passengers) ? route.passengers : [];
      const distance = route.totalDistance;
      const duration = route.totalDuration;
      const originalDistance = route.originalDistance;
      const originalDuration = route.originalDuration;
      const hasOriginal = originalDistance != null && originalDuration != null;
      const extraDistance = hasOriginal ? Number(distance) - Number(originalDistance) : null;
      const extraDuration = hasOriginal ? Number(duration) - Number(originalDuration) : null;
      const sequence = Array.isArray(route.sequence) ? route.sequence : [];
      const mapUrl = route.mapFile
        ? `/api/maps/${encodeURIComponent(route.mapFile)}`
        : null;

      return `
        <article class="route-card">
          <div class="route-card-head">
            <div><p class="eyebrow">DRIVER ROUTE</p><h2>${escapeHTML(route.driverID)}</h2>
              <p>${passengers.length} assigned passenger${passengers.length === 1 ? "" : "s"}</p></div>
            <div class="route-passengers">${passengers.map(id => `<span>${escapeHTML(id)}</span>`).join("")}</div>
          </div>
          <div class="route-metrics">
            <div class="route-metric"><span>Optimised distance</span><strong>${number(distance)} km</strong></div>
            <div class="route-metric"><span>Optimised duration</span><strong>${number(duration)} min</strong></div>
            <div class="route-metric"><span>Original distance</span><strong>${hasOriginal ? `${number(originalDistance)} km` : "—"}</strong></div>
            <div class="route-metric"><span>Original duration</span><strong>${hasOriginal ? `${number(originalDuration)} min` : "—"}</strong></div>
          </div>
          ${hasOriginal ? `<p class="footnote">Additional journey: ${extraDistance >= 0 ? "+" : ""}${number(extraDistance)} km · ${extraDuration >= 0 ? "+" : ""}${number(extraDuration)} min compared with the driver's original route.</p>` : `<p class="footnote">Original route comparison is not included in this saved result. Run AI Matching again after updating the backend to populate it.</p>`}
          <div class="route-sequence"><span class="route-sequence-label">OPTIMISED STOP SEQUENCE</span>
            ${sequence.map((stop, index) => `${index ? `<span class="stop-arrow">→</span>` : ""}<span class="stop-chip">${escapeHTML(formatStop(stop))}</span>`).join("") || `<span class="muted">No stop sequence supplied.</span>`}
          </div>
          ${mapUrl ? `
            <iframe class="route-map-frame" src="${mapUrl}" loading="lazy"
              title="Generated Folium route map for ${escapeHTML(route.driverID)}"
              referrerpolicy="no-referrer"></iframe>
          ` : `
            <div class="map-missing">The saved result does not contain a map filename for this route. Run AI Matching to regenerate the Folium maps and update <code>result.json</code>.</div>
          `}
        </article>
      `;
    }).join("");
  }

  function submitDemoForm(form, kind) {
    form.addEventListener("submit", event => {
      event.preventDefault();
      if (!form.reportValidity()) return;

      const formData = new FormData(form);
      const values = Object.fromEntries(formData.entries());
      const confirmation = $(kind === "find" ? "find-confirmation" : "offer-confirmation");
      const pickup = getLocationName(values.pickup);
      const destination = getLocationName(values.destination);
      const date = values.date ? new Date(`${values.date}T00:00:00`).toLocaleDateString(undefined, {
        day: "numeric", month: "short", year: "numeric"
      }) : "—";
      const time = values.time || "—";
      const isOffer = kind === "offer";

      const details = [
        ["Student", values.studentName],
        [isOffer ? "Starting point" : "Pickup point", pickup],
        ["Destination", destination],
        ["Travel date", date],
        [isOffer ? "Departure time" : "Preferred time", time],
        ...(isOffer ? [["Available seats", `${values.seats} seat${values.seats === "1" ? "" : "s"}`]] : [])
      ];

      confirmation.innerHTML = `
        <div class="confirmation-head"><span class="confirmation-check">✓</span>
          <div><h3>${isOffer ? "Demo ride offer submitted!" : "Demo ride request submitted!"}</h3>
          <p>Your details have been captured for this demonstration.</p></div>
        </div>
        <div class="confirmation-details">${details.map(([label, value]) => `
          <div class="confirmation-detail"><span>${escapeHTML(label)}</span><strong>${escapeHTML(value)}</strong></div>
        `).join("")}</div>
        ${values.note ? `<p class="confirmation-note"><strong>Additional note:</strong> ${escapeHTML(values.note)}</p>` : ""}
        <p class="confirmation-note">This is a temporary demo submission. It has not been added to the CSV dataset and will not affect the AI matching results. You can now view the actual matching results generated from the existing dataset.</p>
        <button class="button button-blue" type="button" data-go="matching">Continue to AI Matching →</button>
      `;
      confirmation.hidden = false;
      confirmation.scrollIntoView({ behavior: "smooth", block: "center" });
      confirmation.querySelector("[data-go]").addEventListener("click", () => navigate("matching"));
    });
  }

  async function loadResults(silent = false) {
    try {
      results = await SmartRideAPI.results();
      renderResults();
      renderRoutes();
      setEngineStatus("Connected · results loaded", true);
      if (!silent) showNotice("Latest AI matching results loaded from the backend.");
      return true;
    } catch (error) {
      results = null;
      renderRoutes();
      setEngineStatus("Connected · no results yet", true);
      if (!silent) showNotice(error.message, true);
      return false;
    }
  }

  async function runMatching() {
    const button = $("run-matching");
    button.disabled = true;
    button.textContent = "Running AI matching…";
    setEngineStatus("Running algorithm…", false);
    showNotice("Processing the existing CSV dataset. Compatibility scoring, Genetic Algorithm and OSRM route optimisation may take a few minutes.");

    try {
      results = await SmartRideAPI.run();
      renderResults();
      renderRoutes();
      setEngineStatus("Connected · latest results ready", true);
      showNotice("AI matching completed. The latest assignments and generated route maps are now available.");
    } catch (error) {
      setEngineStatus("Matching failed", false);
      showNotice(error.message, true);
    } finally {
      button.disabled = false;
      button.innerHTML = "↻ &nbsp;Run AI Matching";
    }
  }

  document.querySelectorAll(".nav").forEach(button =>
    button.addEventListener("click", () => navigate(button.dataset.view))
  );
  document.addEventListener("click", event => {
    const button = event.target.closest("[data-go]");
    if (button) navigate(button.dataset.go);
  });
  $("menu").addEventListener("click", () => $("sidebar").classList.toggle("open"));
  $("run-matching").addEventListener("click", runMatching);
  $("assignment-search").addEventListener("input", renderAssignmentTable);
  submitDemoForm($("find-form"), "find");
  submitDemoForm($("offer-form"), "offer");

  (async function initialise() {
    try {
      locations = normaliseLocations(await SmartRideAPI.locations());
      populateLocationSelects();
      renderLocationDirectory();
    } catch (error) {
      locations = [];
      renderLocationDirectory();
      showNotice(`Campus locations could not be loaded: ${error.message}`, true);
    }
    await loadResults(true);
  })();
})();
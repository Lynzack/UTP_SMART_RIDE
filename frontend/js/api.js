window.SmartRideAPI = {
  async request(url, options = {}) {
    const response = await fetch(url, { cache: "no-store", ...options });
    let payload = {};
    try { payload = await response.json(); } catch (_) {}
    if (!response.ok) {
      throw new Error(payload.error || `Request failed (${response.status})`);
    }
    return payload;
  },
  async results() {
    return this.request("/api/results");
  },
  async run() {
    const payload = await this.request("/api/run-matching", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({})
    });
    return payload.results || payload;
  },
  async locations() {
    return this.request("/api/locations");
  }
};
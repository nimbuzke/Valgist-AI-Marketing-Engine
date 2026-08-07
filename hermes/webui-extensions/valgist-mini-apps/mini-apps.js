/**
 * Valgist Mini-apps — WebUI extension (gallery + launcher).
 *
 * Mini-apps are self-contained HTML files agents save to 04-content/apps/ in the
 * shared workspace (see the shared skill `build-mini-app`). This extension adds a
 * 🧩 rail button that opens a gallery of those apps and runs the selected one in a
 * sandboxed iframe via the WebUI's own /api/file/raw?inline=1 endpoint, which
 * serves HTML with a `sandbox allow-scripts` CSP — no cookies, no parent frame.
 *
 * Ships from the repo at hermes/webui-extensions/ and is projected into
 * data/hermes-home/webui/extensions/ by sync-hermes-webui-profiles.js.
 * It deliberately touches no vendored code: own DOM, own styles, public APIs only.
 */
(function () {
  "use strict";

  var APPS_DIR = "04-content/apps";
  var MAX_APPS = 100;

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function sessionId() {
    try {
      // `S` is the WebUI's top-level session state (classic scripts share scope).
      if (typeof S !== "undefined" && S && S.session && S.session.session_id) {
        return S.session.session_id;
      }
    } catch (e) { /* not booted yet */ }
    return null;
  }

  function rawUrl(sid, relPath) {
    return "/api/file/raw?session_id=" + encodeURIComponent(sid) +
      "&path=" + encodeURIComponent(relPath) + "&inline=1&ts=" + Date.now();
  }

  // ── data ────────────────────────────────────────────────────────────────────

  function listApps(sid) {
    return fetch("/api/list?session_id=" + encodeURIComponent(sid) +
      "&path=" + encodeURIComponent(APPS_DIR), { credentials: "same-origin" })
      .then(function (res) {
        if (res.status === 404) return { entries: [] }; // folder not created yet
        if (!res.ok) throw new Error("list failed (" + res.status + ")");
        return res.json();
      })
      .then(function (data) {
        return (data.entries || [])
          .filter(function (e) { return e.type === "file" && /\.html?$/i.test(e.name); })
          .sort(function (a, b) { return (b.mtime_ns || 0) - (a.mtime_ns || 0); })
          .slice(0, MAX_APPS);
      });
  }

  // Read <title>/<meta> from the app file so cards can say what an app is for.
  function fetchMeta(sid, relPath) {
    return fetch("/api/file?session_id=" + encodeURIComponent(sid) +
      "&path=" + encodeURIComponent(relPath), { credentials: "same-origin" })
      .then(function (res) { return res.ok ? res.json() : null; })
      .then(function (data) {
        if (!data || data.binary || typeof data.content !== "string") return {};
        var head = data.content.slice(0, 4000);
        var title = (head.match(/<title[^>]*>([\s\S]*?)<\/title>/i) || [])[1];
        var meta = function (name) {
          var re = new RegExp("<meta\\s+[^>]*name=[\"']" + name + "[\"'][^>]*>", "i");
          var tag = (head.match(re) || [])[0] || "";
          return ((tag.match(/content=["']([^"']*)["']/i) || [])[1] || "").trim();
        };
        return {
          title: title ? title.replace(/\s+/g, " ").trim() : "",
          description: meta("description"),
          profile: meta("valgist-profile"),
        };
      })
      .catch(function () { return {}; });
  }

  // ── overlay ─────────────────────────────────────────────────────────────────

  var overlay = null;

  function ensureOverlay() {
    if (overlay) return overlay;
    overlay = document.createElement("div");
    overlay.id = "vgMiniAppsOverlay";
    overlay.innerHTML =
      '<div class="vgma-panel" role="dialog" aria-label="Mini-apps">' +
      '  <div class="vgma-head">' +
      '    <button class="vgma-back" type="button" title="Back to gallery" hidden>←</button>' +
      '    <div class="vgma-title">🧩 Mini-apps</div>' +
      '    <a class="vgma-open-full" target="_blank" rel="noopener" hidden>open full ↗</a>' +
      '    <button class="vgma-refresh" type="button" title="Refresh">⟳</button>' +
      '    <button class="vgma-close" type="button" title="Close">✕</button>' +
      "  </div>" +
      '  <div class="vgma-body">' +
      '    <div class="vgma-grid"></div>' +
      '    <div class="vgma-viewer" hidden><iframe sandbox="allow-scripts allow-popups" title="Mini-app"></iframe></div>' +
      "  </div>" +
      "</div>";
    document.body.appendChild(overlay);
    overlay.addEventListener("click", function (e) { if (e.target === overlay) close(); });
    overlay.querySelector(".vgma-close").addEventListener("click", close);
    overlay.querySelector(".vgma-back").addEventListener("click", showGallery);
    overlay.querySelector(".vgma-refresh").addEventListener("click", function () { showGallery(); loadGallery(); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && overlay && overlay.classList.contains("open")) close();
    });
    return overlay;
  }

  function open() {
    ensureOverlay().classList.add("open");
    showGallery();
    loadGallery();
  }

  function close() {
    if (!overlay) return;
    overlay.classList.remove("open");
    // Drop the iframe document so a running app doesn't keep executing.
    overlay.querySelector(".vgma-viewer iframe").src = "about:blank";
  }

  function showGallery() {
    var o = ensureOverlay();
    o.querySelector(".vgma-grid").hidden = false;
    o.querySelector(".vgma-viewer").hidden = true;
    o.querySelector(".vgma-viewer iframe").src = "about:blank";
    o.querySelector(".vgma-back").hidden = true;
    o.querySelector(".vgma-open-full").hidden = true;
    o.querySelector(".vgma-title").textContent = "🧩 Mini-apps";
  }

  function openApp(name, title) {
    var sid = sessionId();
    if (!sid) return;
    var o = ensureOverlay();
    var url = rawUrl(sid, APPS_DIR + "/" + name);
    o.querySelector(".vgma-grid").hidden = true;
    var viewer = o.querySelector(".vgma-viewer");
    viewer.hidden = false;
    viewer.querySelector("iframe").src = url;
    o.querySelector(".vgma-back").hidden = false;
    var full = o.querySelector(".vgma-open-full");
    full.hidden = false;
    full.href = url;
    o.querySelector(".vgma-title").textContent = "🧩 " + (title || name);
  }

  function message(html) {
    ensureOverlay().querySelector(".vgma-grid").innerHTML =
      '<div class="vgma-empty">' + html + "</div>";
  }

  function loadGallery() {
    var sid = sessionId();
    if (!sid) {
      message("Open a chat session first — the gallery reads the session workspace.");
      return;
    }
    message("Loading…");
    listApps(sid).then(function (apps) {
      if (!apps.length) {
        message(
          "No mini-apps yet.<br><br>Ask any profile to build one — e.g. " +
          "<em>“build a mini-app that calculates our Q3 budget split”</em>. " +
          "Agents save them to <code>" + esc(APPS_DIR) + "/</code> (see the " +
          "<code>build-mini-app</code> skill) and they appear here for everyone."
        );
        return;
      }
      var grid = ensureOverlay().querySelector(".vgma-grid");
      grid.innerHTML = apps.map(function (a, i) {
        var when = a.mtime_ns ? new Date(a.mtime_ns / 1e6).toLocaleDateString() : "";
        return (
          '<button class="vgma-card" type="button" data-idx="' + i + '">' +
          '  <div class="vgma-card-title">' + esc(a.name.replace(/\.html?$/i, "")) + "</div>" +
          '  <div class="vgma-card-desc"></div>' +
          '  <div class="vgma-card-meta">' + esc(when) + "</div>" +
          "</button>"
        );
      }).join("");
      grid.querySelectorAll(".vgma-card").forEach(function (card) {
        var app = apps[Number(card.dataset.idx)];
        card.addEventListener("click", function () {
          openApp(app.name, card.querySelector(".vgma-card-title").textContent);
        });
        fetchMeta(sid, APPS_DIR + "/" + app.name).then(function (m) {
          if (m.title) card.querySelector(".vgma-card-title").textContent = m.title;
          if (m.description) card.querySelector(".vgma-card-desc").textContent = m.description;
          if (m.profile) {
            card.querySelector(".vgma-card-meta").textContent =
              (m.profile + " · " + card.querySelector(".vgma-card-meta").textContent).replace(/ · $/, "");
          }
        });
      });
    }).catch(function (err) {
      message("Could not load mini-apps: " + esc(err && err.message ? err.message : err));
    });
  }

  // ── launcher ────────────────────────────────────────────────────────────────

  function mountLauncher() {
    if (document.getElementById("vgMiniAppsBtn")) return;
    var btn = document.createElement("button");
    btn.id = "vgMiniAppsBtn";
    btn.type = "button";
    btn.title = "Mini-apps";
    btn.setAttribute("aria-label", "Mini-apps");
    btn.textContent = "🧩";
    btn.addEventListener("click", open);
    // Prefer a native spot on the left rail; fall back to a floating button.
    var railBtn = document.querySelector(".rail-btn[data-panel]");
    if (railBtn && railBtn.parentElement) {
      btn.className = "rail-btn has-tooltip";
      btn.setAttribute("data-tooltip", "Mini-apps");
      railBtn.parentElement.appendChild(btn);
    } else {
      btn.className = "vgma-float";
      document.body.appendChild(btn);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mountLauncher);
  } else {
    mountLauncher();
  }
})();

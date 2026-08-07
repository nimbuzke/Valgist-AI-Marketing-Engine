/**
 * Valgist World — WebUI extension: the end-user home screen.
 *
 * An isometric cutaway of the Valgist office with a mini dashboard around it.
 * The middle is the world you interact with; the sides carry the numbers, the
 * live task list, the campaigns and what just happened.
 *
 * The artwork IS the render. world.webp is drawn to scale and every hotspot is a
 * percentage rectangle over the image box (hermes/world/rooms.json), so the map
 * tracks the art at any viewport size without layout maths and the art can be
 * regenerated without touching this file.
 *
 * It covers everything except the WebUI's icon rail, which stays reachable on the
 * left. The rail offset is measured from the live DOM; if the rail can't be found
 * it falls back to full width and warns — never throws, never blanks the app.
 *
 * Ships from the repo at hermes/webui-extensions/ and is projected into
 * data/hermes-home/webui/extensions/ by sync-hermes-webui-profiles.js. It touches
 * no vendored code: own DOM, own styles, public APIs only.
 */
(function () {
  "use strict";

  var BASE = "/extensions/valgist-world/";
  var REFRESH_MS = 60000;

  var world = null;      // world.json — rooms + profile metadata, ships with us
  var live = null;       // GET /api/world — counts, tasks, campaigns, activity
  var loadFailed = false;
  var timer = null;
  var reducedMotion = false;
  try {
    reducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  } catch (e) { /* assume motion is fine */ }

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function ago(iso) {
    if (!iso) return "";
    var t = Date.parse(iso);
    if (isNaN(t)) return "";
    var s = Math.max(0, (Date.now() - t) / 1000);
    if (s < 90) return "just now";
    if (s < 5400) return Math.round(s / 60) + "m ago";
    if (s < 172800) return Math.round(s / 3600) + "h ago";
    return Math.round(s / 86400) + "d ago";
  }

  // ── layout ──────────────────────────────────────────────────────────────────

  /**
   * X coordinate where the panel may start: the right edge of the WebUI's icon
   * rail. The rail is the one piece of chrome that has to stay reachable; the
   * conversation sidebar is covered on purpose, because this is a home screen.
   * 0 means "full width", the fail-soft answer when the rail isn't where we think.
   */
  function railOffset() {
    try {
      var rail = document.querySelector("nav.rail");
      if (rail && rail.getBoundingClientRect) {
        var b = rail.getBoundingClientRect();
        if (b.width > 0 && b.width < window.innerWidth * 0.5) return b.right;
      }
    } catch (e) { /* fall through */ }
    console.warn("[valgist-world] could not measure the WebUI rail — rendering full width");
    return 0;
  }

  function applyLayout() {
    var p = document.getElementById("vgWorldPanel");
    if (p) p.style.left = railOffset() + "px";
  }

  var watchersBound = false;
  function bindWatchers() {
    if (watchersBound) return;
    watchersBound = true;
    window.addEventListener("resize", applyLayout);
    try {
      var rail = document.querySelector("nav.rail");
      if (rail && typeof ResizeObserver === "function") new ResizeObserver(applyLayout).observe(rail);
    } catch (e) { /* the resize listener is enough */ }
  }

  // ── data ────────────────────────────────────────────────────────────────────

  function loadWorld() {
    if (world) return Promise.resolve(world);
    return fetch(BASE + "world.json", { credentials: "same-origin" })
      .then(function (r) {
        if (!r.ok) throw new Error("world.json (" + r.status + ")");
        return r.json();
      })
      .then(function (d) { world = d; return world; });
  }

  /** Live numbers from the admin server. Optional: never blocks, never throws. */
  function loadLive() {
    var url = world && world.adminUrl;
    if (!url) return Promise.resolve(null);
    var settled = false;
    return new Promise(function (resolve) {
      var t = setTimeout(function () { if (!settled) { settled = true; resolve(null); } }, 3000);
      fetch(url.replace(/\/$/, "") + "/api/world", { mode: "cors", cache: "no-store" })
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (d) { if (!settled) { settled = true; clearTimeout(t); resolve(d); } })
        .catch(function () { if (!settled) { settled = true; clearTimeout(t); resolve(null); } });
    });
  }

  // ── shell ───────────────────────────────────────────────────────────────────

  function ensurePanel() {
    var p = document.getElementById("vgWorldPanel");
    if (p) return p;
    p = document.createElement("div");
    p.id = "vgWorldPanel";
    p.className = "vgw-panel";
    // Full-bleed scene. Everything else floats over it: a wordmark top-left, a
    // cluster of data icons top-right. The office gets the whole screen because
    // the office is the point — the numbers are one click away, not permanently
    // eating a third of the width.
    p.innerHTML =
      '<div class="vgw-stage" id="vgwStage"></div>' +
      '<div class="vgw-mark"><b>Valgist</b><span id="vgwSub"></span></div>' +
      '<div class="vgw-dock" id="vgwDock" role="toolbar" aria-label="Dashboard"></div>' +
      '<div class="vgw-pop" id="vgwPop" aria-hidden="true"></div>' +
      '<div class="vgw-drawer" id="vgwDrawer" aria-hidden="true"></div>';
    document.body.appendChild(p);
    renderDock();
    bindWatchers();
    return p;
  }

  // ── the data dock ───────────────────────────────────────────────────────────

  var DOCK = [
    { key: "stats", icon: "📊", label: "At a glance" },
    { key: "campaigns", icon: "🎯", label: "Campaigns" },
    { key: "tasks", icon: "📋", label: "Task list" },
    { key: "activity", icon: "🔔", label: "Recently" },
  ];
  var openPop = null;

  function renderDock() {
    var dock = document.getElementById("vgwDock");
    if (!dock) return;
    dock.innerHTML =
      DOCK.map(function (d) {
        return '<button class="vgw-dockbtn" type="button" data-pop="' + d.key + '" title="' + esc(d.label) +
          '" aria-label="' + esc(d.label) + '"><span class="vgw-dockicon">' + d.icon +
          '</span><i class="vgw-dockbadge" data-badge="' + d.key + '"></i></button>';
      }).join("") +
      '<span class="vgw-docksep"></span>' +
      '<button class="vgw-dockbtn" id="vgwRefresh" type="button" title="Refresh the numbers" aria-label="Refresh"><span class="vgw-dockicon">↻</span></button>' +
      '<button class="vgw-dockbtn" id="vgwClose" type="button" title="Close (Esc)" aria-label="Close"><span class="vgw-dockicon">✕</span></button>';
    dock.querySelectorAll("[data-pop]").forEach(function (b) {
      b.addEventListener("click", function (e) {
        e.stopPropagation();
        togglePop(b.getAttribute("data-pop"));
      });
    });
    dock.querySelector("#vgwRefresh").addEventListener("click", function (e) {
      e.stopPropagation();
      var icon = e.currentTarget.querySelector(".vgw-dockicon");
      if (icon) { icon.classList.add("vgw-spin"); setTimeout(function () { icon.classList.remove("vgw-spin"); }, 900); }
      refresh(true);
    });
    dock.querySelector("#vgwClose").addEventListener("click", close);
  }

  function togglePop(key) {
    var pop = document.getElementById("vgwPop");
    if (!pop) return;
    if (openPop === key) return hidePop();
    openPop = key;
    pop.innerHTML = popBody(key);
    pop.classList.add("open");
    pop.setAttribute("aria-hidden", "false");
    document.querySelectorAll(".vgw-dockbtn[data-pop]").forEach(function (b) {
      b.classList.toggle("on", b.getAttribute("data-pop") === key);
    });
    // Clicking a task jumps to the profile that owns it.
    pop.querySelectorAll(".vgw-tasks li[data-owner]").forEach(function (li) {
      var owner = li.getAttribute("data-owner");
      if (!owner || !(world.profiles || {})[owner]) return;
      li.classList.add("vgw-clickable");
      li.title = "Chat with " + (world.profiles[owner].name || owner);
      li.addEventListener("click", function () { chatWith(owner); });
    });
  }

  function hidePop() {
    var pop = document.getElementById("vgwPop");
    openPop = null;
    if (pop) { pop.classList.remove("open"); pop.setAttribute("aria-hidden", "true"); }
    document.querySelectorAll(".vgw-dockbtn[data-pop]").forEach(function (b) { b.classList.remove("on"); });
  }

  // ── the map ─────────────────────────────────────────────────────────────────

  function roomStat(id) {
    return (live && live.rooms && live.rooms[id]) || null;
  }

  function renderMap() {
    var stage = document.getElementById("vgwStage");
    if (!stage) return;

    var frame = document.createElement("div");
    frame.className = "vgw-frame";

    var img = new Image();
    img.className = "vgw-art";
    img.alt = "Isometric cutaway of the Valgist marketing office";
    img.src = BASE + (world.art || "world.webp");
    img.addEventListener("error", function () {
      stage.innerHTML = '<div class="vgw-msg">The office artwork (' + esc(world.art || "world.webp") +
        ") could not be loaded. Every profile is still reachable from the Lobby list and the composer footer.</div>";
    });
    frame.appendChild(img);

    (world.rooms || []).forEach(function (room) {
      frame.appendChild(hotspot(room, false));
    });
    if (world.lobby && world.lobby.rect) {
      frame.appendChild(hotspot({
        id: "__lobby", name: "Lobby", color: "#9fb0cc",
        rect: world.lobby.rect, charter: world.lobby.charter,
        profiles: Object.keys(world.profiles || {}),
      }, true));
    }

    stage.innerHTML = "";
    stage.appendChild(frame);
    bindParallax(frame);
    updateBadges();
  }

  function hotspot(room, isLobby) {
    var r = room.rect || [0, 0, 0, 0];
    var b = document.createElement("button");
    b.type = "button";
    b.className = "vgw-hot" + (isLobby ? " vgw-lobby" : "");
    b.setAttribute("data-room", room.id);
    b.style.left = r[0] + "%";
    b.style.top = r[1] + "%";
    b.style.width = r[2] + "%";
    b.style.height = r[3] + "%";
    b.style.setProperty("--room", room.color || "#4fb7ff");
    b.setAttribute("aria-label", room.name + " — " + (room.profiles || []).length + " profiles");
    b.innerHTML =
      '<span class="vgw-plate">' +
      '  <span class="vgw-plate-name">' + esc(room.name) + "</span>" +
      '  <span class="vgw-plate-meta">' +
      '    <span class="vgw-plate-people">' + (room.profiles || []).length + "</span>" +
      '    <span class="vgw-plate-badges" data-badges="' + esc(room.id) + '"></span>' +
      "  </span>" +
      "</span>";
    // Spotlight: hovering one room dims the others, so the map reads as a place
    // you are pointing at rather than a flat sheet of buttons.
    b.addEventListener("mouseenter", function () { spotlight(room.id); });
    b.addEventListener("focus", function () { spotlight(room.id); });
    b.addEventListener("mouseleave", clearSpotlight);
    b.addEventListener("blur", clearSpotlight);
    b.addEventListener("click", function () { isLobby ? openLobby() : openRoom(room); });
    return b;
  }

  function spotlight(id) {
    var stage = document.getElementById("vgwStage");
    if (stage) stage.setAttribute("data-focus", id);
  }
  function clearSpotlight() {
    var stage = document.getElementById("vgwStage");
    if (stage) stage.removeAttribute("data-focus");
  }

  /** Live counts live on the plates, so the map itself is the first dashboard. */
  function updateBadges() {
    (world.rooms || []).forEach(function (room) {
      var host = document.querySelector('[data-badges="' + room.id + '"]');
      if (!host) return;
      var s = roomStat(room.id);
      var bits = "";
      if (s && s.openOrders) bits += '<i class="vgw-b vgw-b-open" title="' + s.openOrders + ' open work order(s) queued for this room">' + s.openOrders + "</i>";
      if (s && s.blocked) bits += '<i class="vgw-b vgw-b-blocked" title="' + s.blocked + ' work order(s) blocked and waiting on you">' + s.blocked + "</i>";
      if (s && s.documents) bits += '<i class="vgw-b vgw-b-docs" title="' + s.documents + ' document(s) these profiles have written">' + s.documents + "</i>";
      host.innerHTML = bits;
      var btn = document.querySelector('.vgw-hot[data-room="' + room.id + '"]');
      if (btn) btn.classList.toggle("vgw-attention", !!(s && s.blocked));
    });
  }

  /**
   * A few degrees of pointer-follow tilt. Enough that the room you are pointing
   * at feels like a place; small enough that a hotspot never drifts off its art.
   */
  function bindParallax(frame) {
    if (reducedMotion) return;
    var stage = document.getElementById("vgwStage");
    if (!stage) return;
    stage.addEventListener("mousemove", function (e) {
      var box = frame.getBoundingClientRect();
      if (!box.width || !box.height) return;
      var dx = (e.clientX - (box.left + box.width / 2)) / box.width;
      var dy = (e.clientY - (box.top + box.height / 2)) / box.height;
      frame.style.transform = "rotateX(" + (-dy * 2.2).toFixed(2) + "deg) rotateY(" + (dx * 2.6).toFixed(2) + "deg)";
    });
    stage.addEventListener("mouseleave", function () { frame.style.transform = ""; });
  }

  // ── side panels ─────────────────────────────────────────────────────────────

  function offlineNote() {
    return '<div class="vgw-quiet">These numbers come from the Valgist Admin server' +
      (world && world.adminUrl ? " at <code>" + esc(world.adminUrl) + "</code>" : "") +
      ", which isn't answering right now. The office map and every profile still work.</div>";
  }

  function popBody(key) {
    var head = '<h3 class="vgw-pop-title">' +
      esc((DOCK.filter(function (d) { return d.key === key; })[0] || {}).label || "") + "</h3>";
    if (!live) return head + offlineNote();

    if (key === "stats") {
      var t = live.totals || {};
      var tiles = [
        ["Campaigns", t.campaigns, "Documents under 03-campaigns/"],
        ["Open work", t.openOrders, "Work orders waiting to be picked up"],
        ["Blocked", t.blockedOrders, "Work orders stuck — these need you", t.blockedOrders ? "bad" : ""],
        ["Documents", t.documents, "Everything in the knowledge base"],
        ["Reviewed", t.reviewed, "Outputs you have given a verdict on"],
        ["Accepted", t.acceptanceRate == null ? "—" : t.acceptanceRate + "%", "Share of reviewed outputs accepted first time"],
      ];
      return head + '<div class="vgw-tiles">' + tiles.map(function (x) {
        return '<div class="vgw-tile ' + (x[3] || "") + '" title="' + esc(x[2]) + '">' +
          "<b>" + esc(x[1] == null ? "0" : String(x[1])) + "</b><span>" + esc(x[0]) + "</span></div>";
      }).join("") + "</div>";
    }

    if (key === "campaigns") {
      return head + ((live.campaigns || []).length
        ? '<ul class="vgw-list">' + live.campaigns.map(function (c) {
            return "<li><b>" + esc(c.title) + "</b><span>" +
              (c.owner ? esc(c.owner) : "unassigned") + (c.updated ? " · " + esc(c.updated) : "") + "</span></li>";
          }).join("") + "</ul>"
        : '<div class="vgw-quiet">No campaign documents yet. Ask the 🎯 Marketing Director for a quarterly plan and they will start one.</div>');
    }

    if (key === "tasks") {
      return head + ((live.tasks || []).length
        ? '<ul class="vgw-list vgw-tasks">' + live.tasks.map(function (o) {
            return '<li data-owner="' + esc(o.owner || "") + '">' +
              "<b>" + esc(o.title) + "</b>" +
              '<span><i class="vgw-pri vgw-pri-' + esc(String(o.priority || "P2").toLowerCase()) + '">' + esc(o.priority || "P2") + "</i> " +
              esc(o.ownerName || "unassigned") +
              (o.status === "blocked" ? ' · <i class="vgw-blocked">blocked' + (o.blockedOn ? ": " + esc(o.blockedOn) : "") + "</i>" : "") +
              (o.due ? " · due " + esc(o.due) : "") + "</span></li>";
          }).join("") + "</ul>"
        : '<div class="vgw-quiet">No open work orders. Create one in the Admin dashboard\'s Work tab, or just start a chat — a work order is for jobs you want to survive the session.</div>');
    }

    return head + ((live.activity || []).length
      ? '<ul class="vgw-list vgw-feed">' + live.activity.map(function (a) {
          return "<li><b>" + esc(a.detail) + "</b><span>" + (a.who ? esc(a.who) + " · " : "") + esc(ago(a.ts)) + "</span></li>";
        }).join("") + "</ul>"
      : '<div class="vgw-quiet">Nothing has happened yet.</div>');
  }

  /** Counts ride on the dock icons, so the numbers that matter need no click. */
  function updateDockBadges() {
    var t = (live && live.totals) || {};
    var counts = {
      stats: t.blockedOrders || 0,
      campaigns: t.campaigns || 0,
      tasks: (live && live.tasks ? live.tasks.length : 0),
      activity: 0,
    };
    DOCK.forEach(function (d) {
      var el = document.querySelector('[data-badge="' + d.key + '"]');
      if (!el) return;
      var n = counts[d.key];
      el.textContent = n ? String(n) : "";
      el.className = "vgw-dockbadge" + (n ? " on" : "") + (d.key === "stats" && n ? " bad" : "");
    });
    if (openPop) {
      var pop = document.getElementById("vgwPop");
      if (pop) pop.innerHTML = popBody(openPop);
    }
  }

  // ── room drawer ─────────────────────────────────────────────────────────────

  function profileCard(id, roomColor) {
    var p = (world.profiles || {})[id] || { name: id };
    var reads = (p.reads || []).slice(0, 6).map(function (c) {
      return '<code>' + esc(c) + "</code>";
    }).join(" ");
    var conn = (p.connectors || []);
    var connHtml = conn.length
      ? conn.map(function (c) {
          return '<span class="vgw-conn ' + (c.wired ? "on" : "off") + '" title="' +
            (c.wired ? "Connected" : "Not wired — this profile works from files you give it") + '">' +
            esc(c.name) + "</span>";
        }).join("")
      : '<span class="vgw-conn none" title="Needs no external system">works from the knowledge base alone</span>';
    var sig = (p.signatureSkills || []).slice(0, 4).map(function (s) {
      return '<span class="vgw-skill">' + esc(s) + "</span>";
    }).join("");
    return (
      '<div class="vgw-card" style="--room:' + esc(roomColor || "#4fb7ff") + '">' +
      '  <div class="vgw-card-head">' +
      '    <span class="vgw-emoji">' + esc(p.emoji || "🎭") + "</span>" +
      '    <span class="vgw-name">' + esc(p.name || id) + "</span>" +
      '    <button class="vgw-chat" type="button" data-profile="' + esc(id) + '">Chat →</button>' +
      "  </div>" +
      (p.tagline ? '  <div class="vgw-tagline">' + esc(p.tagline) + "</div>" : "") +
      (reads ? '  <div class="vgw-facet"><span class="vgw-facet-k">Reads first</span><span class="vgw-facet-v">' + reads + "</span></div>" : "") +
      '  <div class="vgw-facet"><span class="vgw-facet-k">Connectors</span><span class="vgw-facet-v">' + connHtml + "</span></div>" +
      (sig ? '  <div class="vgw-facet"><span class="vgw-facet-k">Can do</span><span class="vgw-facet-v">' + sig + "</span></div>" : "") +
      "</div>"
    );
  }

  function showDrawer(title, subtitle, color, bodyHtml) {
    var d = document.getElementById("vgwDrawer");
    if (!d) return;
    d.innerHTML =
      '<div class="vgw-drawer-head" style="--room:' + esc(color || "#4fb7ff") + '">' +
      '  <div><div class="vgw-drawer-title">' + esc(title) + "</div>" +
      (subtitle ? '  <div class="vgw-drawer-sub">' + esc(subtitle) + "</div>" : "") + "</div>" +
      '  <button class="vgw-x" type="button" aria-label="Close">×</button>' +
      "</div>" +
      '<div class="vgw-drawer-body">' + bodyHtml + "</div>";
    d.querySelector(".vgw-x").addEventListener("click", hideDrawer);
    d.querySelectorAll(".vgw-chat").forEach(function (b) {
      b.addEventListener("click", function () { chatWith(b.getAttribute("data-profile")); });
    });
    d.classList.add("open");
    d.setAttribute("aria-hidden", "false");
  }

  function hideDrawer() {
    var d = document.getElementById("vgwDrawer");
    if (!d) return;
    d.classList.remove("open");
    d.setAttribute("aria-hidden", "true");
  }

  function openRoom(room) {
    var s = roomStat(room.id);
    // Plain english, because "0 open work orders" tells a new user nothing.
    var strip = s
      ? '<div class="vgw-strip">' +
        "<span>" + (s.openOrders
          ? "<b>" + s.openOrders + "</b> job" + (s.openOrders === 1 ? "" : "s") + " queued for this room"
          : "No queued jobs") + "</span>" +
        (s.blocked ? '<span class="bad"><b>' + s.blocked + "</b> blocked, waiting on you</span>" : "") +
        "<span>" + (s.documents
          ? "<b>" + s.documents + "</b> document" + (s.documents === 1 ? "" : "s") + " written so far"
          : "Nothing written yet") + "</span>" +
        "</div>"
      : "";
    var cards = (room.profiles || []).map(function (id) { return profileCard(id, room.color); }).join("");
    showDrawer(room.name, room.charter, room.color, strip + cards);
  }

  function openLobby() {
    var ids = Object.keys(world.profiles || {}).sort(function (a, b) {
      return (world.profiles[a].name || a).localeCompare(world.profiles[b].name || b);
    });
    showDrawer("Lobby", (world.lobby && world.lobby.charter) || "", "#9fb0cc",
      '<div class="vgw-search"><input type="search" id="vgwFind" placeholder="Filter all ' + ids.length + ' profiles…" autocomplete="off"></div>' +
      '<div id="vgwLobbyList">' + ids.map(function (id) { return profileCard(id, "#7f8aa3"); }).join("") + "</div>");
    var input = document.getElementById("vgwFind");
    if (!input) return;
    input.focus();
    input.addEventListener("input", function () {
      var q = input.value.trim().toLowerCase();
      document.querySelectorAll("#vgwLobbyList .vgw-card").forEach(function (c) {
        c.style.display = !q || c.textContent.toLowerCase().indexOf(q) !== -1 ? "" : "none";
      });
    });
  }

  // ── actions ─────────────────────────────────────────────────────────────────

  function chatWith(id) {
    if (!id) return;
    close();
    // `switchToProfile` owns the whole switch dance (session embargo, sidebar
    // repaint, cookie). Call it and let it decide about sessions — re-implementing
    // any of that here would fight the WebUI, not help it.
    try {
      if (typeof switchToProfile === "function") {
        Promise.resolve(switchToProfile(id))
          .then(function () { if (typeof switchPanel === "function") switchPanel("chat"); })
          .catch(function (e) { console.warn("[valgist-world] profile switch failed", e); });
        return;
      }
    } catch (e) { /* reported below */ }
    console.warn("[valgist-world] switchToProfile() unavailable — cannot open a chat for " + id);
  }

  function setSub(text) {
    var s = document.getElementById("vgwSub");
    if (s) s.textContent = text;
  }

  function refresh(manual) {
    if (!world) return;
    if (manual) setSub("Refreshing…");
    return loadLive().then(function (d) {
      live = d;
      updateBadges();
      updateDockBadges();
      setSub((world.rooms || []).length + " departments · " +
        Object.keys(world.profiles || {}).length + " profiles" +
        (live ? "" : " · dashboard offline"));
    });
  }

  function open() {
    var p = ensurePanel();
    applyLayout();
    p.classList.add("open");
    document.addEventListener("keydown", onKey);
    if (loadFailed) world = null;

    if (world) {
      refresh(false);
    } else {
      var stage = document.getElementById("vgwStage");
      if (stage) stage.innerHTML = '<div class="vgw-msg">Opening the office…</div>';
      loadWorld()
        .then(function () { return loadLive(); })
        .then(function (d) {
          loadFailed = false;
          live = d;
          renderMap();
          updateDockBadges();
          setSub((world.rooms || []).length + " departments · " +
            Object.keys(world.profiles || {}).length + " profiles" +
            (live ? "" : " · dashboard offline"));
        })
        .catch(function (err) {
          loadFailed = true;
          console.warn("[valgist-world]", err);
          var st = document.getElementById("vgwStage");
          if (st) {
            st.innerHTML = '<div class="vgw-msg">Could not load the office map (' +
              esc(err && err.message ? err.message : String(err)) +
              "). The profile picker in the composer footer still works.</div>";
          }
        });
    }
    if (timer) clearInterval(timer);
    timer = setInterval(function () { refresh(false); }, REFRESH_MS);
    document.addEventListener("click", onDocClick, true);
  }

  function close() {
    var p = document.getElementById("vgWorldPanel");
    if (p) p.classList.remove("open");
    hideDrawer();
    hidePop();
    document.removeEventListener("keydown", onKey);
    document.removeEventListener("click", onDocClick, true);
    if (timer) { clearInterval(timer); timer = null; }
  }

  /**
   * The panel covers the WebUI, but the rail and sidebar underneath it stay
   * interactive — so clicking Chat or Tasks used to load the panel *behind* the
   * office and look like nothing happened. Anything clicked outside this panel
   * is the user asking to go somewhere else: get out of the way.
   *
   * Capture phase, so we close before the WebUI's own handler runs. We do not
   * swallow the event — the click still does what the user asked.
   */
  function onDocClick(e) {
    var panel = document.getElementById("vgWorldPanel");
    if (!panel || !panel.classList.contains("open")) return;
    var t = e.target;
    if (panel.contains(t)) {
      // Inside the panel: a click on the scene backdrop dismisses an open popover.
      if (openPop && !t.closest(".vgw-pop") && !t.closest(".vgw-dock")) hidePop();
      return;
    }
    if (t.closest && t.closest("#vgWorldBtn")) return; // our own launcher toggles
    close();
  }

  function onKey(e) {
    if (e.key !== "Escape") return;
    var d = document.getElementById("vgwDrawer");
    if (d && d.classList.contains("open")) hideDrawer();
    else if (openPop) hidePop();
    else close();
  }

  // ── launcher ────────────────────────────────────────────────────────────────

  function mountLauncher() {
    if (document.getElementById("vgWorldBtn")) return;
    var btn = document.createElement("button");
    btn.id = "vgWorldBtn";
    btn.type = "button";
    btn.title = "The office";
    btn.setAttribute("aria-label", "The office");
    btn.textContent = "🌍";
    btn.addEventListener("click", function () {
      var p = document.getElementById("vgWorldPanel");
      if (p && p.classList.contains("open")) close(); else open();
    });
    // First in the rail: this is the home screen, so it sits above Chat.
    var railBtn = document.querySelector(".rail-btn[data-panel]");
    if (railBtn && railBtn.parentElement) {
      btn.className = "rail-btn has-tooltip";
      btn.setAttribute("data-tooltip", "The office");
      railBtn.parentElement.insertBefore(btn, railBtn);
    } else {
      btn.className = "vgw-float";
      document.body.appendChild(btn);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mountLauncher);
  } else {
    mountLauncher();
  }
})();

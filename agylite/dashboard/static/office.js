// Agent Office (P23, D-043): draws the pixel office from /api/agents and polls while the page is visible.
// Every string from the API is inserted with textContent (event text is data, never markup).
"use strict";
const W = 480, H = 300;
const SKIN = ["#f1c27d", "#e0ac69", "#c68642", "#8d5524", "#ffdbac"];
const SHIRT = ["#2563eb", "#0d9488", "#db2777", "#b91c1c", "#7c3aed", "#475569", "#ca8a04", "#16a34a", "#0369a1",
  "#9a3412", "#e11d48", "#9333ea", "#0891b2", "#4d7c0f", "#c026d3", "#15803d", "#be123c", "#ea580c", "#0284c7"];
const HAIR = ["#111827", "#3f2a1d", "#7c2d12", "#1f2937", "#4b2e1a", "#a16207", "#e5e7eb", "#854d0e"];
const FLOOR = {front: ["#efe6d6", "#e8dcc8"], engineering: ["#d8c3a0", "#cfb895"], design: ["#e3d6ef", "#d8c9e8"],
  qa: ["#cfe6d6", "#c2ddca"], seomedia: ["#cfe0ee", "#c1d6e8"], mentors: ["#dcdcdc", "#d0d0d0"]};
const LABEL = {working: "working", idle: "idle", waiting: "waiting", blocked: "blocked", off: "off · on request",
  disabled: "disabled by policy"};
const $ = (id) => document.getElementById(id);
const cv = $("cv"), g = cv.getContext("2d"), ov = $("ov"), bar = $("bar");
let seats = [], rooms = [], selected = null, frame = 0, built = false;
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

function hash(s) { let h = 7; for (const c of s) h = (h * 31 + c.charCodeAt(0)) >>> 0; return h; }
function el(tag, cls, text) { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
const pct = (v, m) => (v / m * 100) + "%";
const R = (x, y, w, h, c) => { g.fillStyle = c; g.fillRect(x | 0, y | 0, w | 0, h | 0); };

function drawRoom(r) {
  const [a, b] = FLOOR[r.id] || ["#ddd", "#d2d2d2"];
  R(r.x, r.y, r.w, r.h, a);
  for (let y = r.y; y < r.y + r.h; y += 8) for (let x = r.x + ((y / 8) % 2 ? 4 : 0); x < r.x + r.w; x += 8) R(x, y, 4, 4, b);
}
function plant(x, y) { R(x + 1, y + 6, 6, 5, "#9a3412"); R(x + 1, y, 6, 5, "#16a34a"); R(x, y + 2, 8, 2, "#15803d"); R(x + 3, y - 1, 2, 2, "#22c55e"); }
function person(s, f) {
  const x = s.x, y = s.y, h = hash(s.id);
  if (s.state === "disabled") { R(x + 1, y + 10, 22, 7, "#3f3f46"); R(x + 15, y + 5, 6, 5, "#27272a"); return; }
  const skin = SKIN[h % SKIN.length], shirt = SHIRT[h % SHIRT.length], hair = HAIR[(h >> 3) % HAIR.length];
  const working = s.state === "working", bob = working && f % 2 ? 1 : 0;
  R(x + 7, y + 1 - bob, 8, 8, skin); R(x + 7, y - bob, 8, 3, hair); R(x + 6, y + 1 - bob, 1, 4, hair); R(x + 15, y + 1 - bob, 1, 4, hair);
  if (s.state === "off") { R(x + 9, y + 5, 2, 1, "#1f2937"); R(x + 12, y + 5, 2, 1, "#1f2937"); }
  else { R(x + 9, y + 4 - bob, 1, 2, "#1f2937"); R(x + 12, y + 4 - bob, 1, 2, "#1f2937"); }
  R(x + 6, y + 9, 10, 6, shirt);
  const arm = working ? (f % 2 ? 0 : 1) : 0; R(x + 4, y + 10 + arm, 2, 4, shirt); R(x + 16, y + 11 - arm, 2, 4, shirt);
  R(x + 1, y + 13, 22, 6, "#8b5a2b"); R(x + 1, y + 13, 22, 1, "#a87444"); R(x + 2, y + 19, 2, 3, "#5b3a1d"); R(x + 20, y + 19, 2, 3, "#5b3a1d");
  const glow = working ? (f % 2 ? "#4ade80" : "#86efac") : s.state === "blocked" ? "#f87171" : s.state === "waiting" ? "#fde68a" : "#64748b";
  R(x + 16, y + 7, 7, 6, "#1f2937"); R(x + 17, y + 8, 5, 4, glow); R(x + 18, y + 13, 3, 1, "#1f2937"); R(x + 5, y + 14, 6, 2, "#e5e7eb");
  if (s.state === "off") { R(x + 18, y - 6, 3, 1, "#e5e7eb"); R(x + 19, y - 5, 1, 1, "#e5e7eb"); R(x + 18, y - 4, 3, 1, "#e5e7eb"); }
}
function draw() {
  R(0, 0, W, H, "#3b2f2a");
  rooms.forEach(drawRoom);
  [24, 70, 320, 366, 412].forEach((x) => { R(x, 6, 22, 6, "#7dd3fc"); R(x + 10, 6, 2, 6, "#e0f2fe"); });
  [[12, 124], [284, 124], [310, 124], [458, 124], [12, 270], [140, 270], [170, 270], [318, 270], [458, 270]].forEach(([x, y]) => plant(x, y));
  R(392, 206, 30, 14, "#b45309"); R(392, 206, 30, 2, "#d97706");
  seats.forEach((s) => person(s, frame));
}

function build() {
  ov.replaceChildren(); [...bar.querySelectorAll(".chip")].forEach((c) => c.remove());
  rooms.forEach((r) => { const d = el("div", "room", r.name); d.style.left = pct(r.x + r.w / 2, W); d.style.top = pct(r.y + 2, H); ov.append(d); });
  seats.forEach((s) => {
    const t = el("button", "tag", s.name); t.type = "button"; t.id = "tag-" + s.id; t.append(el("span", "d"));
    t.style.left = pct(s.x + 12, W); t.style.top = pct(s.y - 2, H); t.addEventListener("click", () => select(s.id)); ov.append(t);
    const b = el("div", "bubble"); b.id = "bub-" + s.id; b.hidden = true; b.style.left = pct(s.x + 12, W); b.style.top = pct(s.y - 11, H); ov.append(b);
    const c = el("button", "chip"); c.type = "button"; c.id = "chip-" + s.id; c.append(el("i"), document.createTextNode(s.name + " "), el("em"));
    c.addEventListener("click", () => select(s.id)); bar.append(c);
  });
  built = true;
}
function render() {
  seats.forEach((s) => {
    const t = $("tag-" + s.id), b = $("bub-" + s.id), c = $("chip-" + s.id);
    if (!t) return;
    t.dataset.s = s.state; t.classList.toggle("sel", s.id === selected);
    b.hidden = !s.say; b.textContent = s.say || ""; b.classList.toggle("crit", s.state === "blocked");
    c.dataset.s = s.state; c.querySelector("em").textContent = LABEL[s.state] || s.state;
  });
  const s = seats.find((x) => x.id === selected) || seats[0];
  if (!s) return;
  const card = $("card"); card.replaceChildren(el("h2", null, s.name));
  const dl = el("dl", "kv");
  const st = el("span", "state " + s.state, LABEL[s.state] || s.state);
  [["Status", st], ["Capabilities", (s.caps || []).join(", ") || (s.core ? "agylite route (OS core)" : "specialist personas")],
   ["Knowledge from", (s.sources || []).join(", ") || (s.core ? "Agylite" : "—")],
   ["Room", (rooms.find((r) => r.id === s.room) || {}).name || s.room], ["Now", s.say || "at desk, nothing routed"],
   ["Last event", s.last || "—"]].forEach(([k, v]) => { dl.append(el("dt", null, k)); const dd = el("dd"); dd.append(v); dl.append(dd); });
  card.append(dl, el("p", "hint", s.state === "disabled" ? "Disabled for every project by config/verification.yaml: an exception can only be recorded; no browser is driven."
    : s.state === "off" ? "Runs only when you ask for it." : "Agents work only when the router selects their capability; idle agents cost no context."));
}
function select(id) { selected = id; render(); }

async function get(path) { const r = await fetch(path, {cache: "no-store"}); if (!r.ok) throw new Error(path + " " + r.status); return r.json(); }
async function poll() {
  try {
    const a = await get("api/agents");
    const shape = a.seats.map((s) => s.id).join();
    seats = a.seats; rooms = a.rooms;
    if (!built || shape !== bar.dataset.shape) { bar.dataset.shape = shape; build(); }
    if (!selected) selected = (seats.find((s) => s.state === "working") || seats[0]).id;
    $("clock").textContent = new Date(a.at).toLocaleTimeString();
    const mode = $("mode"); mode.textContent = a.demo ? "demo replay" : "live"; mode.className = "pill " + (a.demo ? "demo" : "live");
    render(); draw();
    const log = $("log"); log.replaceChildren();
    (await get("api/activity")).items.forEach((it) => {
      const row = el("div"); row.append(el("time", null, new Date(it.ts).toLocaleTimeString()), el("span", null, it.text),
        el("span", "state " + (it.severity === "high" || it.severity === "critical" ? "blocked" : "idle"), it.severity));
      log.append(row);
    });
  } catch (e) { $("sub").textContent = "Cannot reach the dashboard server (" + e.message + "). It stops when idle: run `agylite dashboard` again."; }
}
async function once() {
  try {
    const s = await get("api/state");
    $("sub").textContent = [s.project, s.branch && "branch " + s.branch, s.bundle && "bundle " + s.bundle,
      s.phase && s.phase + " (" + s.phase_status + ")"].filter(Boolean).join(" · ");
    const fill = (id, rows, f) => { const box = $(id); box.replaceChildren(); rows.forEach((r) => { const d = el("div"); f(r).forEach((x) => d.append(x)); box.append(d); }); };
    const cls = (st) => st === "ready" || st === "RUNTIME_VERIFIED" || st === "INSTALLED" ? "working" : st === "broken" ? "blocked" : "idle";
    fill("hosts", (await get("api/hosts")).hosts, (h) => [el("span", null, h.host), el("span", "state " + cls(h.status), h.status)]);
    fill("runtimes", (await get("api/runtimes")).runtimes, (r) => [el("span", null, r.runtime + (r.version ? " · " + r.version : "")), el("span", "state " + cls(r.status), r.status)]);
  } catch (e) { /* poll() reports connection problems */ }
}
once(); poll();
setInterval(() => { if (!document.hidden) poll(); }, 2000);
if (!reduce) setInterval(() => { if (!document.hidden && seats.length) { frame++; draw(); } }, 280);

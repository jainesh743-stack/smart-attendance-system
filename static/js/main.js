/**
 * Smart Attendance System - Main JS
 * Handles: Dark/Light theme toggle, anti-cheat, tab detection
 */

document.addEventListener("DOMContentLoaded", () => {

  // ── Theme Toggle ─────────────────────────────────────────────
  const savedTheme = localStorage.getItem("theme") || "light";
  document.documentElement.setAttribute("data-theme", savedTheme);
  updateThemeIcon(savedTheme);

  const btn = document.getElementById("themeToggle");
  if (btn) {
    btn.addEventListener("click", () => {
      const cur  = document.documentElement.getAttribute("data-theme");
      const next = cur === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      localStorage.setItem("theme", next);
      updateThemeIcon(next);
    });
  }

  function updateThemeIcon(theme) {
    const icon = document.getElementById("themeIcon");
    if (icon) icon.className = theme === "dark" ? "bi bi-moon-fill" : "bi bi-sun-fill";
  }

  // ── Page load fade ───────────────────────────────────────────
  document.querySelector("main")?.classList.add("page-enter");
  const s = document.createElement("style");
  s.textContent = `
    .page-enter { animation: pageIn .35s ease both; }
    @keyframes pageIn { from { opacity:0; transform:translateY(10px); } to { opacity:1; transform:none; } }
  `;
  document.head.appendChild(s);

});

// Toast helper (available globally)
window.showToast = function(msg, type = "info") {
  document.querySelectorAll(".sa-toast").forEach(t => t.remove());
  const colors = { success: "#22c55e", error: "#ef4444", info: "#3b82f6", warning: "#f59e0b" };
  const icons  = { success: "check-circle-fill", error: "x-circle-fill", info: "info-circle-fill", warning: "exclamation-circle-fill" };
  const toast  = document.createElement("div");
  toast.className = "sa-toast";
  toast.style.cssText = `
    position:fixed;top:72px;right:20px;z-index:9999;
    background:var(--card);border:1px solid ${colors[type]};
    color:var(--text);padding:12px 18px;border-radius:10px;
    display:flex;align-items:center;gap:10px;
    font-family:'Outfit',sans-serif;font-size:.88rem;
    box-shadow:0 8px 24px rgba(0,0,0,.15);max-width:320px;
    animation:toastIn .3s cubic-bezier(.34,1.56,.64,1);
  `;
  toast.innerHTML = `<i class="bi bi-${icons[type]}" style="color:${colors[type]};font-size:1rem;flex-shrink:0"></i><span>${msg}</span>`;
  const st = document.createElement("style");
  st.textContent = "@keyframes toastIn{from{transform:translateX(100%);opacity:0}to{transform:none;opacity:1}}";
  document.head.appendChild(st);
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
};

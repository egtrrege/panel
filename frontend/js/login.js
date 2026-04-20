/**
 * login.js — Login page logic.
 * Handles form submission, error display, and particle animation.
 */
document.addEventListener("DOMContentLoaded", () => {

  // Redirect to dashboard if already logged in
  API.redirectIfLoggedIn();

  // ── Particles ──────────────────────────────────────────────
  const particleContainer = document.getElementById("particles");
  if (particleContainer) {
    for (let i = 0; i < 40; i++) {
      const p = document.createElement("div");
      p.className = "particle";
      p.style.left = Math.random() * 100 + "%";
      p.style.top  = (80 + Math.random() * 30) + "%";
      p.style.animationDuration = (6 + Math.random() * 10) + "s";
      p.style.animationDelay   = (Math.random() * 8) + "s";
      p.style.width  = (1.5 + Math.random() * 2) + "px";
      p.style.height = p.style.width;
      particleContainer.appendChild(p);
    }
  }

  // ── Login form ─────────────────────────────────────────────
  const form     = document.getElementById("loginForm");
  const errorBox = document.getElementById("loginError");
  const btn      = document.getElementById("loginBtn");
  const btnText  = btn.querySelector(".btn-text");
  const btnSpin  = btn.querySelector(".btn-spinner");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorBox.classList.add("hidden");

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    if (!username || !password) {
      errorBox.textContent = "Please enter username and password";
      errorBox.classList.remove("hidden");
      return;
    }

    // Show spinner
    btnText.classList.add("hidden");
    btnSpin.classList.remove("hidden");
    btn.disabled = true;

    try {
      const data = await API.post("/auth/login", { username, password });
      API.setToken(data.token, data.username);
      window.location.href = "/dashboard.html";
    } catch (err) {
      errorBox.textContent = err.message || "Invalid credentials";
      errorBox.classList.remove("hidden");
    } finally {
      btnText.classList.remove("hidden");
      btnSpin.classList.add("hidden");
      btn.disabled = false;
    }
  });
});

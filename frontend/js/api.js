/**
 * api.js — Shared API client for MC Panel frontend.
 * Manages JWT token storage and provides fetch wrappers.
 */
const API = (() => {
  const TOKEN_KEY = "mc_panel_token";
  const USER_KEY  = "mc_panel_user";

  function getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }

  function setToken(token, username) {
    localStorage.setItem(TOKEN_KEY, token);
    if (username) localStorage.setItem(USER_KEY, username);
  }

  function clearToken() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }

  function getUsername() {
    return localStorage.getItem(USER_KEY) || "admin";
  }

  function isLoggedIn() {
    return !!getToken();
  }

  /** Redirect to login if no token */
  function requireAuth() {
    if (!isLoggedIn()) {
      window.location.href = "/index.html";
    }
  }

  /** Redirect to dashboard if already logged in */
  function redirectIfLoggedIn() {
    if (isLoggedIn()) {
      window.location.href = "/dashboard.html";
    }
  }

  /** Core fetch wrapper with auth header */
  async function request(method, path, body = null) {
    const headers = { "Content-Type": "application/json" };
    const token = getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    const opts = { method, headers };
    if (body) opts.body = JSON.stringify(body);

    const resp = await fetch(`/api${path}`, opts);

    // If 401, token is expired — redirect to login
    if (resp.status === 401) {
      clearToken();
      window.location.href = "/index.html";
      throw new Error("Session expired");
    }

    const data = await resp.json();
    if (!resp.ok) {
      throw new Error(data.detail || `HTTP ${resp.status}`);
    }
    return data;
  }

  // Convenience methods
  const get  = (path) => request("GET", path);
  const post = (path, body) => request("POST", path, body);

  return {
    getToken, setToken, clearToken, getUsername,
    isLoggedIn, requireAuth, redirectIfLoggedIn,
    get, post,
  };
})();

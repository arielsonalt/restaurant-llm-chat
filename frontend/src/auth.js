const KEY = "auth_tokens";

export function setTokens(tokens) {
  localStorage.setItem(KEY, JSON.stringify(tokens));
}
export function getTokens() {
  const raw = localStorage.getItem(KEY);
  return raw ? JSON.parse(raw) : null;
}
export function logout() {
  localStorage.removeItem(KEY);
}

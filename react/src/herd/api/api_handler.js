async function refreshAccessToken() {
  const refreshToken = localStorage.getItem("refresh");

  if (!refreshToken) {
    return null;
  }

  const response = await fetch("/api/token/refresh/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      refresh: refreshToken,
    }),
  });

  if (!response.ok) {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    window.location.href = "/login";
    return null;
  }

  const data = await response.json();
  localStorage.setItem("access", data.access);

  return data.access;
}

export async function api(path, options = {}) {
  let accessToken = localStorage.getItem("access");

  let response = await fetch(path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...options.headers,
    },
  });

  if (response.status === 401) {
    accessToken = await refreshAccessToken();

    if (!accessToken) {
      return response;
    }

    response = await fetch(path, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
        ...options.headers,
      },
    });
  }

  return response;
}
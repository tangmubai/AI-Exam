export default {
  fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/practice" || url.pathname === "/practice/") {
      url.pathname = "/practice.html";
      return env.STATIC_ASSETS.fetch(new Request(url, request));
    }

    return env.STATIC_ASSETS.fetch(request);
  }
};


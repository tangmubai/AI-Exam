export default {
  fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/practice" || url.pathname === "/practice/") {
      url.pathname = "/practice.html";
      return env.ASSETS.fetch(new Request(url, request));
    }

    return env.ASSETS.fetch(request);
  }
};

const { createProxyMiddleware } = require("http-proxy-middleware");

const options = {
  target: "http://127.0.0.1:8000",
  headers: {
    "X-Forwarded-User": "dev",
    "X-Forwarded-Preferred-Username": "dev",
    "X-Forwarded-Email": "dev@jlzhou.me",
  },
  changeOrigin: true,
  ws: true,
};

const apiProxy = createProxyMiddleware("/api", options);

module.exports = function (app) {
  app.use("/api", apiProxy);
};

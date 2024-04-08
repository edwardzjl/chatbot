const { createProxyMiddleware } = require("http-proxy-middleware");

const apiProxy = createProxyMiddleware({
  target: "http://127.0.0.1:8000",
  pathFilter: '/api',
  headers: {
    "X-Forwarded-User": "dev",
    "X-Forwarded-Preferred-Username": "dev",
    "X-Forwarded-Email": "dev@jlzhou.me",
  },
  changeOrigin: true,
  ws: true,
});

module.exports = function (app) {
  app.use(apiProxy);
};

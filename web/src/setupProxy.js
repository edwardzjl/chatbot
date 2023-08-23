const { createProxyMiddleware } = require("http-proxy-middleware");

const options = {
  target: "http://127.0.0.1:8000",
  headers: {
    "kubeflow-userid": "dev",
  },
  changeOrigin: true,
  ws: true,
};

const apiProxy = createProxyMiddleware("/api", options);

module.exports = function (app) {
  app.use("/api", apiProxy);
};

const { createProxyMiddleware } = require("http-proxy-middleware");

const options = {
  target: "http://localhost:8000",
  headers: {
    "kubeflow-userid": "dev",
  },
};

const apiProxy = createProxyMiddleware("/api", options);

module.exports = function (app) {
  app.use("/api", apiProxy);
};

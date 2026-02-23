const path = require("path");

function getAxios() {
  try {
    return require("axios");
  } catch (error) {
    const fallback = path.resolve(__dirname, "../../../../web/frontend/node_modules/axios");
    return require(fallback);
  }
}

module.exports = getAxios;

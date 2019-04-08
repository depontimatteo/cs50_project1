
  document.addEventListener("DomContentLoaded", () => {
      var socket = io.connect(location.protocol + "//" + document.domain + ":" + location.port);

      socket.on("connect", () => {
          document.querySelectorAll("button").forEach(button => {
              button.onclick = () => {
                  socket.emit("evento");
              };
          });
      });
  }
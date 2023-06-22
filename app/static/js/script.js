window.addEventListener("DOMContentLoaded", (event) => {
    console.log("DOM fully loaded and parsed");
    const message = document.getElementById("message");
    const button = document.getElementById("button");
    const link = document.getElementById("file_link");
    var socket = io.connect();

    //receive details from server
    socket.on("scan_result", function (msg) {
      if (msg.status === "denied") {
        console.log("Access Denied");
        message.innerHTML = msg.message;
        message.classList.remove("message-allowed");
        message.classList.remove("message-info");
        message.classList.add("message-denied");

        button.classList.remove("visible");
        button.classList.add("hidden");

        link.href = "#"

      } else if (msg.status === "granted") {
        console.log("Access Granted");
        message.innerHTML = msg.message;
        message.classList.remove("message-denied");
        message.classList.remove("message-info");
        message.classList.add("message-allowed");

        button.classList.remove("hidden");
        button.classList.add("visible");

        link.href = Flask.url_for("display_pdf", {"file_id": msg.file_id})


      } else {
        message.innerHTML = msg.message;
        message.classList.remove("message-denied");
        message.classList.remove("message-allowed");
        message.classList.add("message-info");

        button.classList.remove("visible");
        button.classList.add("hidden");

        link.href = "#"
      }
    });
  });
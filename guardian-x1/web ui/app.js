// WebSockets connection to the Guardian API will go here
console.log("Guardian X-1 Web UI loaded.");
const cellularState = document.getElementById('cellular-state');

socket.onmessage = function(event) {
  const data = JSON.parse(event.data);
  if (data.type === "cellular_status") {
    cellularState.innerText = data.status;
  }
};

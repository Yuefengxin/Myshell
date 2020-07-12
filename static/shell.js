const MAX_LINES = 9999999;

Terminal.applyAddon(fullscreen)
Terminal.applyAddon(fit)
Terminal.applyAddon(webLinks)
Terminal.applyAddon(search)
const term = new Terminal({
      cursorBlink: true,
      macOptionIsMeta: true,
      scrollback: true,
  });
term.open(document.getElementById('terminal'));
term.fit()
term.setOption("scrollback", MAX_LINES);
//console.log(`size: ${term.cols} columns, ${term.rows} rows`)
term.write("Welcome to Shell!\n")
term.on('key', (key, ev) => {
  console.log("pressed key", key)
  console.log("event", ev)
  socket.emit("pty-input", {"input": key})
});

const socket = io.connect('/pty');
const status = document.getElementById("status")

socket.on("pty-output", function(data){
  console.log("new output", data)
  term.write(data.output)
})

socket.on("connect", () => {
  status.innerHTML = '<span style="background-color: lightgreen;">connected</span>'
  }
)

socket.on("disconnect", () => {
  status.innerHTML = '<span style="background-color: #ff8383;">disconnected</span>'
})

window.addEventListener("resize", () => {
    term.fit();
});

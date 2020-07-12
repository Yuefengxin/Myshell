#!/usr/bin/env python3
import argparse
from flask import Flask, render_template
from flask_socketio import SocketIO
import pty
import os
import subprocess
import select
import shlex


__version__ = "0.4.0.1"

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
app.config["fd"] = None
app.config["child_pid"] = None
socketio = SocketIO(app)

def read_and_forward_pty_output():
    max_read_bytes = 1024 * 20
    while True:
        socketio.sleep(0.01)
        if app.config["fd"]:
            timeout_sec = 0
            (data_ready, _, _) = select.select([app.config["fd"]], [], [], timeout_sec)
            if data_ready:
                output = os.read(app.config["fd"], max_read_bytes).decode()
                socketio.emit("pty-output", {"output": output}, namespace="/pty")


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("pty-input", namespace="/pty")
def pty_input(data):
    if app.config["fd"]:
        # print("writing to ptd: %s" % data["input"])
        os.write(app.config["fd"], data["input"].encode())

@socketio.on("connect", namespace="/pty")
def connect():

    if app.config["child_pid"]:
        # already started child process, don't start another
        return

    # create child process attached to a pty we can read from and write to
    (child_pid, fd) = pty.fork()
    if child_pid == 0:
        # this is the child process fork.
        # anything printed here will show up in the pty, including the output
        # of this subprocess
        subprocess.run(app.config["cmd"])
    else:
        # this is the parent process fork.
        # store child fd and pid
        app.config["fd"] = fd
        app.config["child_pid"] = child_pid
        cmd = " ".join(shlex.quote(c) for c in app.config["cmd"])
        print("child pid is", child_pid)
        print(
            f"starting background task with command `{cmd}` "
        )
        socketio.start_background_task(target=read_and_forward_pty_output)
        print("task started")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "A fully functional terminal in your browser. "
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-p", "--port", default=8000, help="port to run server on")
    parser.add_argument("--debug", action="store_true", help="debug the server")
    parser.add_argument("--version", action="store_true", help="print version and exit")
    parser.add_argument(
        "--command", default="zsh", help="Command to run in the terminal"
    )
    parser.add_argument(
        "--cmd-args",
        default="",
        help="arguments to pass to command (i.e. --cmd-args='arg1 arg2 --flag')",
    )
    args = parser.parse_args()
    if args.version:
        print(__version__)
        exit(0)
    print(f"serving on http://127.0.0.1:{args.port}")
    app.config["cmd"] = [args.command] + shlex.split(args.cmd_args)
    socketio.run(app, debug=args.debug, port=int(args.port))


if __name__ == "__main__":
    main()

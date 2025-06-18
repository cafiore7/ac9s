import subprocess
from threading import Thread

class LogStreamer:
    def __init__(self, container_id, callback):
        self.container_id = container_id
        self.callback = callback

    def start(self):
        def stream():
            try:
                p = subprocess.Popen(
                    ["container", "logs", self.container_id, "--follow"],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT
                )
                for line in iter(p.stdout.readline, b''):
                    colored = self.colorize(line.decode("utf-8").rstrip())
                    self.callback(colored)
            except Exception as e:
                self.callback(f"Error: {e}")

        Thread(target=stream, daemon=True).start()

    def colorize(self, line):
        if "ERROR" in line:
            return f"[red]{line}[/red]"
        if "WARN" in line or "WARNING" in line:
            return f"[yellow]{line}[/yellow]"
        if "INFO" in line:
            return f"[green]{line}[/green]"
        return line

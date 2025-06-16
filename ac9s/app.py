import platform
import subprocess
import json
from textual.app import App, ComposeResult
from textual.widgets import Static, DataTable, Log
from textual.containers import Vertical
from textual.reactive import reactive
from ac9s.model import ContainerModel
from ac9s.control import ContainerControl

REFRESH_INTERVAL = 3
AC9S_VERSION = "v0.4.9.8"

class AC9sApp(App):
    THEME = "nord-dark"
    mode = reactive("table")

    def __init__(self):
        super().__init__()
        self.model = ContainerModel()
        self.selected_container = ""
        self.full_logs = []

    def compose(self) -> ComposeResult:
        header = Static(self.build_header(), id="header")
        header.styles.height = 3
        header.styles.padding_bottom = 1
        yield header

        with Vertical(id="main_view"):
            self.container_table = DataTable(zebra_stripes=True)
            self.container_table.add_columns("ID", "Image", "OS", "Arch", "State", "IP")
            self.container_table.show_cursor = True
            self.container_table.cursor_type = "cell"
            self.container_table.cursor_movement = "row"
            self.container_table.allow_highlight = True
            self.container_table.styles.width = "100%"
            self.container_table.styles.height = "100%"
            yield self.container_table

            self.log_window = Log(highlight=True)
            self.log_window.styles.width = "100%"
            self.log_window.styles.height = "100%"
            self.log_window.display = False
            yield self.log_window

        self.footer = Static("", id="footer")
        yield self.footer

    async def on_mount(self):
        self.refresh_table()
        self.set_interval(REFRESH_INTERVAL, self.refresh_table)
        self.set_focus(self.container_table)

    def build_header(self):
        macos_version = platform.mac_ver()[0]
        return (
            f"[b][yellow]AC9s[/yellow][/b] | [cyan]{AC9S_VERSION}[/cyan] | "
            f"[green]macOS {macos_version}[/green] | "
            "[b]Keys:[/b] "
            "[blue]↑↓[/blue] Nav "
            "[red]l[/red] Logs "
            "[red]Enter[/red] Description "
            "[red]s[/red] Start "
            "[red]t[/red] Stop "
            "[red]d[/red] Delete "
            "[red]q[/red] Quit"
        )


    def refresh_table(self):
        selected_id = None
        if self.container_table.cursor_row is not None:
            try:
                row = self.container_table.get_row_at(self.container_table.cursor_row)
                selected_id = row[0]
            except:
                pass

        self.model.update()
        self.container_table.clear()

        for cid, info in self.model.containers.items():
            self.container_table.add_row(cid, info["image"], info["os"], info["arch"], info["state"], info["ip"])

        if selected_id:
            for idx, _ in enumerate(self.container_table.rows):
                if self.container_table.get_row_at(idx)[0] == selected_id:
                    self.container_table.cursor_coordinate = (idx, 0)
                    break
            else:
                if self.container_table.row_count > 0:
                    self.container_table.cursor_coordinate = (0, 0)
        elif self.container_table.row_count > 0:
            self.container_table.cursor_coordinate = (0, 0)

        header = self.build_header() + f" | [white]Containers: {len(self.model.containers)}[/white]"
        self.query_one("#header", Static).update(header)
        self.update_footer()

    def update_footer(self):
        running = self.model.running_count()
        total_cpus = self.model.total_cpus()
        total_mem = self.model.total_memory_mb()
        self.footer.update(f"Running: {running} | CPUs: {total_cpus} | RAM: {total_mem} MB")

    def load_logs_for_selection(self):
        if self.container_table.row_count == 0 or self.container_table.cursor_row is None:
            return

        row = self.container_table.get_row_at(self.container_table.cursor_row)
        cid = row[0]
        self.selected_container = cid
        self.mode = "logs"

        self.log_window.clear()
        self.container_table.display = False
        self.log_window.display = True

        try:
            logs_output = subprocess.check_output(
                ["container", "logs", cid],
                stderr=subprocess.STDOUT
            )
            decoded_logs = logs_output.decode().replace('\r', '')
            logs = decoded_logs.splitlines()
            for line in logs:
                self.log_window.write_line(line)
        except subprocess.CalledProcessError as e:
            self.log_window.write_line(f"Error: {e.output.decode()}")

    def load_description_for_selection(self):
        if self.container_table.row_count == 0 or self.container_table.cursor_row is None:
            return

        row = self.container_table.get_row_at(self.container_table.cursor_row)
        cid = row[0]
        self.selected_container = cid
        self.display_description(cid)

    def display_logs(self, container_id):
        self.full_logs = []
        self.log_window.clear()
        self.container_table.display = False
        self.log_window.display = True

        try:
            logs_output = subprocess.check_output(
                ["container", "logs", container_id],
                stderr=subprocess.STDOUT
            )
            logs = logs_output.decode().splitlines()
            for line in logs:
                self.log_window.write(line)
        except subprocess.CalledProcessError as e:
            self.log_window.write(f"Error: {e.output.decode()}")

    def display_description(self, container_id):
        self.full_logs = []
        self.log_window.clear()
        self.container_table.display = False
        self.log_window.display = True

        try:
            desc_output = subprocess.check_output(
                ["container", "inspect", container_id],
                stderr=subprocess.STDOUT
            )
            desc_json = json.loads(desc_output.decode())
            pretty = json.dumps(desc_json, indent=4)

            for line in pretty.splitlines():
                self.log_window.write_line(line)
        except subprocess.CalledProcessError as e:
            self.log_window.write(f"Error: {e.output.decode()}")

    def on_key(self, event):
        if self.mode == "table":
            if self.container_table.row_count == 0 or self.container_table.cursor_row is None:
                return

            row = self.container_table.get_row_at(self.container_table.cursor_row)
            cid = row[0]

            if event.key == "s":
                ContainerControl.start(cid)
            elif event.key == "t":
                ContainerControl.stop(cid)
            elif event.key == "d":
                ContainerControl.delete(cid)
            elif event.key == "l":
                self.mode = "logs"
                self.load_logs_for_selection()
            elif event.key == "enter":
                self.mode = "description"
                self.load_description_for_selection()
            elif event.key == "q":
                self.exit()

        elif self.mode in ["logs", "description"]:
            if event.key in ["escape", "q"]:
                self.mode = "table"
                self.log_window.display = False
                self.container_table.display = True
                self.set_focus(self.container_table)

def main():
    AC9sApp().run()

if __name__ == "__main__":
    main()

import subprocess
import json

class ContainerModel:
    def __init__(self):
        self.containers = {}

    def update(self):
        output = subprocess.check_output(["container", "ls", "--format", "json"])
        data = json.loads(output.decode())

        self.containers = {}
        for entry in data:
            config = entry["configuration"]
            container_id = config.get("id") or config.get("hostname")
            image = config.get("image", {}).get("reference", "unknown")
            os = config.get("platform", {}).get("os", "unknown")
            arch = config.get("platform", {}).get("architecture", "unknown")
            state = entry.get("status", "unknown")
            ip = "N/A"
            if entry.get("networks"):
                ip = entry["networks"][0].get("address", "N/A")

            cpus = config.get("resources", {}).get("cpus", 0)
            memory = config.get("resources", {}).get("memoryInBytes", 0)

            self.containers[container_id] = {
                "image": image,
                "os": os,
                "arch": arch,
                "state": state,
                "ip": ip,
                "cpus": cpus,
                "memory": memory
            }

    def running_count(self):
        return sum(1 for c in self.containers.values() if c["state"] == "running")

    def total_cpus(self):
        return sum(c["cpus"] for c in self.containers.values())

    def total_memory_mb(self):
        return sum(c["memory"] for c in self.containers.values()) // (1024 * 1024)

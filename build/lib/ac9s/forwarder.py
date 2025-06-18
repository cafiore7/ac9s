import subprocess
import os

class PortForwarder:
    @staticmethod
    def forward(local_port, container_ip, container_port):
        cmd = f"socat TCP-LISTEN:{local_port},fork TCP:{container_ip}:{container_port}"
        print(f"Forwarding localhost:{local_port} -> {container_ip}:{container_port}")
        subprocess.Popen(cmd, shell=True)

import subprocess

class ContainerControl:

    @staticmethod
    def start(container_id):
        subprocess.run(["container", "start", container_id])

    @staticmethod
    def stop(container_id):
        subprocess.run(["container", "stop", container_id])

    @staticmethod
    def delete(container_id):
        subprocess.run(["container", "delete", container_id])

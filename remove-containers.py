import subprocess
import json

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

# Get all containers
output = run("container list --format json")

try:
    containers = json.loads(output)
except json.JSONDecodeError:
    print("No containers found or container service not running.")
    containers = []

if not containers:
    print("No containers to delete.")
else:
    for c in containers:
        cid = c['configuration']['id']
        print(f"Deleting container: {cid}")
        run(f"container delete {cid}")

print("✅ All Apple containers have been removed.")

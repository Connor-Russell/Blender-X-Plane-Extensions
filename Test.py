import os
import subprocess
from datetime import datetime

# Define paths
cd = os.getcwd()
TestDir = os.path.join(cd, "Tests")
OutputTestDir = os.path.join(cd, "Tests")
DateAndTime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")

#If quick test, only the first version will be used
QuickTest = True

TestExport =            True
TestImport =            True
InternalTest =          False #This is EOL, and this stuff is inherently testedin the import/export tests
TestBaker =             True
TestInApp =             True
TestNormalConversion =  True

def run_blender(blender_exe, script):
    subprocess.run([
        blender_exe,
        "--background",
        "--python", script
    ], shell=True, cwd=TestDir)

def test_all(blender_exe):
    if TestExport:
        run_blender(blender_exe, os.path.join(TestDir, "export_tests.py"))
    if TestImport:
        run_blender(blender_exe, os.path.join(TestDir, "import_tests.py"))
    if InternalTest:
        run_blender(blender_exe, os.path.join(TestDir, "internal_tests.py"))
    if TestBaker:
        run_blender(blender_exe, os.path.join(TestDir, "bake_test.py"))
    if TestInApp:
        run_blender(blender_exe, os.path.join(TestDir, "in_app_tests.py"))
    if TestNormalConversion:
        run_blender(blender_exe, os.path.join(TestDir, "normal_conversion.py"))

#Run python build.py (same dir as this)
subprocess.run(["python", "build.py"], cwd=cd)

# Remove old result file
results_path = os.path.join(OutputTestDir, "Test Results.csv")
try:
    os.remove(results_path)
except FileNotFoundError:
    pass

#Load the BlenderVersions.txt file from the test dir. Add to the blender_exe list
blender_exes = []

with open(os.path.join(TestDir, "BlenderVersions.txt"), "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue  # Skip comments and empty lines
        tokens = line.strip().split(",")
        if len(tokens) < 2:
            continue  # Skip lines that don't have enough tokens
        name = tokens[0].strip()
        path = tokens[1].strip()
        blender_exes.append([name, path])

# Create new results file
with open(results_path, "w", encoding="utf-8") as f:
    f.write(f"{DateAndTime}\nTest Name,Result,Percentage,Message\n")

# Run the tests for each version
def add_result_header(header):
    with open(results_path, "a", encoding="utf-8") as f:
        f.write(f"{header}\n")

for exe in blender_exes:
    add_result_header(f"{exe[0]} Tests")
    test_all(exe[1])
    if QuickTest:
        break

# Open the result file (platform-specific)
if os.name == "nt":
    os.startfile(results_path)
else:
    subprocess.run(["open", results_path])

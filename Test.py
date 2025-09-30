import os
import subprocess
from datetime import datetime

# Define paths
cd = os.getcwd()
TestDir = os.path.join(cd, "Tests")
OutputTestDir = os.path.join(cd, "Tests")
DateAndTime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
BlenderFileExporter = os.path.join(cd, "Tests", "Content", "Exporter.blend")
BlenderFileImporter = os.path.join(cd, "Tests", "Content", "Importer.blend")
BlenderFileInternalTests = os.path.join(cd, "Tests", "Content", "InternalTests.blend")
BlenderFileBakeTest = os.path.join(cd, "Tests", "Content", "BakeTest.blend")

# Blender version locations
BlenderExe29 = r"D:\Blender Versions\2.93\blender.exe"
BlenderExe30 = r"D:\Blender Versions\3.01\blender.exe"
BlenderExe31 = r"D:\Blender Versions\3.12\blender.exe"
BlenderExe32 = r"D:\Blender Versions\3.22\blender.exe"
BlenderExe33 = r"D:\Blender Versions\3.39\blender.exe"
BlenderExe34 = r"D:\Blender Versions\3.41\blender.exe"
BlenderExe35 = r"D:\Blender Versions\3.51\blender.exe"
BlenderExe36 = r"D:\Blender Versions\3.69\blender.exe"
BlenderExe40 = r"D:\Blender Versions\4.02\blender.exe"
BlenderExe41 = r"D:\Blender Versions\4.11\blender.exe"
BlenderExe42 = r"D:\Blender Versions\4.23\blender.exe"
BlenderExe43 = r"D:\Blender Versions\4.32\blender.exe"
BlenderExe44 = r"D:\Blender Versions\4.43\blender.exe"

# Bools to control what versions are tested
QuickTest = True
Test29 = True
Test30 = True and not QuickTest
Test31 = True and not QuickTest
Test32 = True and not QuickTest
Test33 = True and not QuickTest
Test34 = True and not QuickTest
Test35 = True and not QuickTest
Test36 = True and not QuickTest
Test40 = True and not QuickTest
Test41 = True and not QuickTest
Test42 = True and not QuickTest
Test43 = True and not QuickTest
Test44 = True and not QuickTest

TestExport =            True
TestImport =            True
InternalTest =          True
TestBaker =             True
TestInApp =             True

def run_blender(blender_exe, blend_file, script):
    subprocess.run([
        blender_exe,
        "--background",
        blend_file,
        "--python", script
    ], shell=True)

def test_all(blender_exe):
    if TestExport:
        run_blender(blender_exe, BlenderFileExporter, os.path.join(TestDir, "export_tests.py"))
    if TestImport:
        run_blender(blender_exe, BlenderFileImporter, os.path.join(TestDir, "import_tests.py"))
    if InternalTest:
        run_blender(blender_exe, BlenderFileInternalTests, os.path.join(TestDir, "internal_tests.py"))
    if TestBaker:
        run_blender(blender_exe, BlenderFileBakeTest, os.path.join(TestDir, "bake_test.py"))
    if TestInApp:
        run_blender(blender_exe, BlenderFileImporter, os.path.join(TestDir, "in_app_tests.py"))

#Run python build.py (same dir as this)
subprocess.run(["python", "build.py"], cwd=cd)

# Remove old result file
results_path = os.path.join(OutputTestDir, "Test Results.csv")
try:
    os.remove(results_path)
except FileNotFoundError:
    pass

# Create new results file
with open(results_path, "w", encoding="utf-8") as f:
    f.write(f"{DateAndTime}\nTest Name,Result,Percentage,Message\n")

# Run the tests for each version
def add_result_header(header):
    with open(results_path, "a", encoding="utf-8") as f:
        f.write(f"{header}\n")

if Test29:
    add_result_header("2.9 Tests")
    test_all(BlenderExe29)
if Test30:
    add_result_header("3.0 Tests")
    test_all(BlenderExe30)
if Test31:
    add_result_header("3.1 Tests")
    test_all(BlenderExe31)
if Test32:
    add_result_header("3.2 Tests")
    test_all(BlenderExe32)
if Test33:
    add_result_header("3.3 Tests")
    test_all(BlenderExe33)
if Test34:
    add_result_header("3.4 Tests")
    test_all(BlenderExe34)
if Test35:
    add_result_header("3.5 Tests")
    test_all(BlenderExe35)
if Test36:
    add_result_header("3.6 Tests")
    test_all(BlenderExe36)
if Test40:
    add_result_header("4.0 Tests")
    test_all(BlenderExe40)
if Test41:
    add_result_header("4.1 Tests")
    test_all(BlenderExe41)
if Test42:
    add_result_header("4.2 Tests")
    test_all(BlenderExe42)
if Test43:
    add_result_header("4.3 Tests")
    test_all(BlenderExe43)
if Test44:
    add_result_header("4.4 Tests")
    test_all(BlenderExe44)

# Open the result file (platform-specific)
if os.name == "nt":
    os.startfile(results_path)
else:
    subprocess.run(["open", results_path])

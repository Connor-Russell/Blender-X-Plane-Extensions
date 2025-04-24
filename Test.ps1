#Define paths
$cd = Get-Location
$TestDir = "$cd\Tests"
$OutputTestDir = "$cd\Tests"
$DateAndTime = Get-Date -Format "yyyy-MM-dd HH-mm-ss"
$BlenderFile = "$cd\Tests\Content\FacadeExporter.blend"

#Define Blender version locations
$BlenderExe29 = "D:\Blender Versions\2.93\blender.exe"
$BlenderExe30 = "D:\Blender Versions\3.01\blender.exe"
$BlenderExe31 = "D:\Blender Versions\3.12\blender.exe"
$BlenderExe32 = "D:\Blender Versions\3.22\blender.exe"
$BlenderExe33 = "D:\Blender Versions\3.39\blender.exe"
$BlenderExe34 = "D:\Blender Versions\3.41\blender.exe"
$BlenderExe35 = "D:\Blender Versions\3.51\blender.exe"
$BlenderExe36 = "D:\Blender Versions\3.69\blender.exe"
$BlenderExe40 = "D:\Blender Versions\4.02\blender.exe"
$BlenderExe41 = "D:\Blender Versions\4.11\blender.exe"
$BlenderExe42 = "D:\Blender Versions\4.23\blender.exe"

#Define bools to control what versions are tested
$Test29 = $true
$Test30 = $true
$Test31 = $true
$Test32 = $true
$Test33 = $true
$Test34 = $true
$Test35 = $true
$Test36 = $true
$Test40 = $true
$Test41 = $true
$Test42 = $true

#First run build our build script, which is in the same folder as this script
& "$cd\Build.ps1"


#Exporter function. Opens Blender, runs the export script and compares the results
function Test-Exporter {
    param (
        [string]$BlenderExe
    )

    #Remove the old exported .fac
    #Remove-Item "$OutputTestDir\Exporter.fac" -ErrorAction SilentlyContinue

    #Launch Blender and run the export and compare test
    & $BlenderExe --background $BlenderFile --python "$TestDir\export_fac_test.py"

    #Remove the old exported .fac
    #Remove-Item "$OutputTestDir\Exporter.fac" -ErrorAction SilentlyContinue
}

#Remove the old result file
Remove-Item "$OutputTestDir\Test Results.csv" -ErrorAction SilentlyContinue

#Creat the new results file, starting with the text "Test Name,Result"
Add-Content "$OutputTestDir\Test Results.csv" "$DateAndTime`nTest Name,Result"

#Run the tests

#2.9 Tests
if ($Test29) {
    Add-Content "$OutputTestDir\Test Results.csv" "2.9 Tests"
    Test-Exporter -BlenderExe $BlenderExe29
}

#3.0 Tests
if ($Test30) {
    Add-Content "$OutputTestDir\Test Results.csv" "3.0 Tests"
    Test-Exporter -BlenderExe $BlenderExe30
}

#3.1 Tests
if ($Test31) {
    Add-Content "$OutputTestDir\Test Results.csv" "3.1 Tests"
    Test-Exporter -BlenderExe $BlenderExe31
}

#3.2 Tests
if ($Test32) {
    Add-Content "$OutputTestDir\Test Results.csv" "3.2 Tests"
    Test-Exporter -BlenderExe $BlenderExe32
}

#3.3 Tests
if ($Test33) {
    Add-Content "$OutputTestDir\Test Results.csv" "3.3 Tests"
    Test-Exporter -BlenderExe $BlenderExe33
}

#3.4 Tests
if ($Test34) {
    Add-Content "$OutputTestDir\Test Results.csv" "3.4 Tests"
    Test-Exporter -BlenderExe $BlenderExe34
}

#3.5 Tests
if ($Test35) {
    Add-Content "$OutputTestDir\Test Results.csv" "3.5 Tests"
    Test-Exporter -BlenderExe $BlenderExe35
}

#3.6 Tests
if ($Test36) {
    Add-Content "$OutputTestDir\Test Results.csv" "3.6 Tests"
    Test-Exporter -BlenderExe $BlenderExe36
}

#4.0 Tests
if ($Test40) {
    Add-Content "$OutputTestDir\Test Results.csv" "4.0 Tests"
    Test-Exporter -BlenderExe $BlenderExe40
}

#4.1 Tests
if ($Test41) {
    Add-Content "$OutputTestDir\Test Results.csv" "4.1 Tests"
    Test-Exporter -BlenderExe $BlenderExe41
}

#4.2 Tests
if ($Test42) {
    Add-Content "$OutputTestDir\Test Results.csv" "4.2 Tests"
    Test-Exporter -BlenderExe $BlenderExe42
}

#Open the result file
Invoke-Item "$OutputTestDir\Test Results.csv"
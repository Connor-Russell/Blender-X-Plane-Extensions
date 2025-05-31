#Define paths
$cd = Get-Location
$TestDir = "$cd\Tests"
$OutputTestDir = "$cd\Tests"
$DateAndTime = Get-Date -Format "yyyy-MM-dd HH-mm-ss"
$BlenderFileFacadeExporter = "$cd\Tests\Content\FacadeExporter.blend"
$BlenderFileLineExporter = "$cd\Tests\Content\LineExporter.blend"
$BlenderFilePolygonExporter = "$cd\Tests\Content\PolygonExporter.blend"
$BlenderFileInternalTests = "$cd\Tests\Content\InternalTests.blend"
$BlenderFileBakeTest = "$cd\Tests\Content\BakeTest.blend"
$BlenderFileImportObject = "$cd\Tests\Content\ObjImporter.blend"
$BlenderFileImportFacade = "$cd\Tests\Content\FacadeExporter.blend"
$BlenderFileImportLine = "$cd\Tests\Content\LineExporter.blend"
$BlenderFileImportPolygon = "$cd\Tests\Content\PolygonExporter.blend"

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
$BlenderExe43 = "D:\Blender Versions\4.32\blender.exe"
$BlenderExe44 = "D:\Blender Versions\4.43\blender.exe"

#Define bools to control what versions are tested
$Test29 = $true
$Test30 = $false
$Test31 = $false
$Test32 = $false
$Test33 = $false
$Test34 = $false
$Test35 = $false
$Test36 = $false
$Test40 = $false
$Test41 = $false
$Test42 = $false
$Test43 = $false
$Test44 = $false

$TestExportFacade =     $true
$TestExportLine =       $true
$TestExportPolygon =    $true
$TestImportObject =     $true
$TestImportFacade =     $true
$TestImportLine =       $true
$TestImportPolygon =    $true
$InternalTest =         $true
$TestBaker =            $true

#First run build our build script, which is in the same folder as this script
& "$cd\Build.ps1"


#Exporter function. Opens Blender, runs the export script and compares the results
function Test-All {
    param (
        [string]$BlenderExe
    )

    #Launch Blender and run the export and compare test
    if ($TestExportFacade)
    {
        & $BlenderExe --background $BlenderFileFacadeExporter --python "$TestDir\export_fac_test.py"
    }
    if ($TestExportLine)
    {
        & $BlenderExe --background $BlenderFileLineExporter --python "$TestDir\export_lin_test.py"
    }
    if ($TestExportPolygon)
    {
        & $BlenderExe --background $BlenderFilePolygonExporter --python "$TestDir\export_pol_test.py"
    }
    if ($InternalTest)
    {
        & $BlenderExe --background $BlenderFileInternalTests --python "$TestDir\internal_tests.py"
    }
    if ($TestBaker)
    {
        & $BlenderExe --background $BlenderFileBakeTest --python "$TestDir\bake_test.py"
    }
    if ($TestImportObject)
    {
        & $BlenderExe --background $BlenderFileImportObject --python "$TestDir\import_obj_test.py"
    }
    if ($TestImportFacade)
    {
        & $BlenderExe --background $BlenderFileImportFacade --python "$TestDir\import_fac_test.py"
    }
    if ($TestImportLine)
    {
        & $BlenderExe --background $BlenderFileImportLine --python "$TestDir\import_lin_test.py"
    }
    if ($TestImportPolygon)
    {
        & $BlenderExe --background $BlenderFileImportPolygon --python "$TestDir\import_pol_test.py"
    }
}

#Remove the old result file
Remove-Item "$OutputTestDir\Test Results.csv" -ErrorAction SilentlyContinue

#Creat the new results file, starting with the text "Test Name,Result"
Add-Content "$OutputTestDir\Test Results.csv" "$DateAndTime`nTest Name,Result"

#Run the tests

#2.9 Tests
if ($Test29) {
    Add-Content "$OutputTestDir\Test Results.csv" "2.9 Tests"
    Test-All -BlenderExe $BlenderExe29
}

#3.0 Tests
if ($Test30) {
    Add-Content "$OutputTestDir\Test Results.csv" "3.0 Tests"
    Test-All -BlenderExe $BlenderExe30
}

#3.1 Tests
if ($Test31) {
    Add-Content "$OutputTestDir\Test Results.csv" "3.1 Tests"
    Test-All -BlenderExe $BlenderExe31
}

#3.2 Tests
if ($Test32) {
    Add-Content "$OutputTestDir\Test Results.csv" "3.2 Tests"
    Test-All -BlenderExe $BlenderExe32
}

#3.3 Tests
if ($Test33) {
    Add-Content "$OutputTestDir\Test Results.csv" "3.3 Tests"
    Test-All -BlenderExe $BlenderExe33
}

#3.4 Tests
if ($Test34) {
    Add-Content "$OutputTestDir\Test Results.csv" "3.4 Tests"
    Test-All -BlenderExe $BlenderExe34
}

#3.5 Tests
if ($Test35) {
    Add-Content "$OutputTestDir\Test Results.csv" "3.5 Tests"
    Test-All -BlenderExe $BlenderExe35
}

#3.6 Tests
if ($Test36) {
    Add-Content "$OutputTestDir\Test Results.csv" "3.6 Tests"
    Test-All -BlenderExe $BlenderExe36
}

#4.0 Tests
if ($Test40) {
    Add-Content "$OutputTestDir\Test Results.csv" "4.0 Tests"
    Test-All -BlenderExe $BlenderExe40
}

#4.1 Tests
if ($Test41) {
    Add-Content "$OutputTestDir\Test Results.csv" "4.1 Tests"
    Test-All -BlenderExe $BlenderExe41
}

#4.2 Tests
if ($Test42) {
    Add-Content "$OutputTestDir\Test Results.csv" "4.2 Tests"
    Test-All -BlenderExe $BlenderExe42
}

#4.3 Tests
if ($Test43) {
    Add-Content "$OutputTestDir\Test Results.csv" "4.3 Tests"
    Test-All -BlenderExe $BlenderExe43
}

#4.4 Tests
if ($Test44) {
    Add-Content "$OutputTestDir\Test Results.csv" "4.4 Tests"
    Test-All -BlenderExe $BlenderExe44
}

#Open the result file
Invoke-Item "$OutputTestDir\Test Results.csv"
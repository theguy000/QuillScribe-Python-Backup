# QuillScribe Nuitka Build Script (PowerShell)
# Builds executable using Nuitka for optimized native performance

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  QuillScribe Nuitka Build Script" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if a command exists
function Test-CommandExists {
    param($Command)
    try {
        Get-Command $Command -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

# Check if Python is available
if (-not (Test-CommandExists "python")) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Python version:" -ForegroundColor Green
python --version

# Check if Nuitka is installed
try {
    python -c "import nuitka" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Nuitka not found"
    }
}
catch {
    Write-Host "Installing Nuitka..." -ForegroundColor Yellow
    pip install nuitka ordered-set zstandard
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install Nuitka" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}
if (Test-Path "run.build") {
    Remove-Item -Recurse -Force "run.build"
}
if (Test-Path "run.dist") {
    Remove-Item -Recurse -Force "run.dist"
}
if (Test-Path "run.onefile-build") {
    Remove-Item -Recurse -Force "run.onefile-build"
}
if (Test-Path "QuillScribe.exe") {
    Remove-Item -Force "QuillScribe.exe"
}
if (Test-Path "QuillScribe-Installer.exe") {
    Remove-Item -Force "QuillScribe-Installer.exe"
}

# Clean Nuitka compilation cache only (preserve compiler downloads)
# Only remove ccache and module cache, NOT the downloads (MinGW64, depends.exe, etc.)
Write-Host "Cleaning Nuitka compilation cache (preserving compiler)..." -ForegroundColor Yellow
$nuitkaCachePath = "$env:LOCALAPPDATA\Nuitka\Nuitka\Cache"
if (Test-Path $nuitkaCachePath) {
    # Only clean ccache and module caches, preserve downloads
    if (Test-Path "$nuitkaCachePath\ccache") {
        Write-Host "Removing ccache..." -ForegroundColor DarkGray
        Remove-Item -Recurse -Force "$nuitkaCachePath\ccache" -ErrorAction SilentlyContinue
    }
    if (Test-Path "$nuitkaCachePath\bytecode") {
        Write-Host "Removing bytecode cache..." -ForegroundColor DarkGray
        Remove-Item -Recurse -Force "$nuitkaCachePath\bytecode" -ErrorAction SilentlyContinue
    }
    # Preserve: downloads, dll-dependencies, etc.
    Write-Host "Preserved compiler downloads (MinGW64 will not be re-downloaded)" -ForegroundColor Green
}

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Build the executable with Nuitka
Write-Host "Building executable with Nuitka..." -ForegroundColor Yellow
Write-Host "This will take several minutes on first build (compiling to native code)..." -ForegroundColor Yellow
Write-Host "Nuitka will automatically download MinGW64 compiler if needed..." -ForegroundColor Cyan

# Set PYTHONPATH to include src directory so Nuitka can find quillscribe package
$env:PYTHONPATH = "$PWD\src;$env:PYTHONPATH"

# Construct the Nuitka command with all options
$nuitkaArgs = @(
    "-m", "nuitka",
    "--standalone",
    "--onefile",
    "--windows-console-mode=disable",
    "--enable-plugin=pyside6",
    "--windows-icon-from-ico=src\quillscribe\icons\app_logo.ico",
    "--include-data-dir=src\quillscribe\icons=icons",
    "--include-data-dir=src\sounds=sounds",
    "--include-package=quillscribe",
    "--nofollow-import-to=PyQt5",
    "--nofollow-import-to=PyQt6",
    "--nofollow-import-to=torch",
    "--nofollow-import-to=torchvision",
    "--nofollow-import-to=torchaudio",
    "--nofollow-import-to=tensorflow",
    "--nofollow-import-to=keras",
    "--nofollow-import-to=matplotlib",
    "--nofollow-import-to=scipy",
    "--nofollow-import-to=pandas",
    "--nofollow-import-to=tkinter",
    "--nofollow-import-to=test",
    "--nofollow-import-to=tests",
    "--nofollow-import-to=unittest",
    "--nofollow-import-to=mypy",
    "--nofollow-import-to=PIL",
    "--nofollow-import-to=psutil",
    "--nofollow-import-to=aioquic",
    "--nofollow-import-to=brotlicffi",
    "--nofollow-import-to=websockets",
    "--output-filename=QuillScribe.exe",
    "--company-name=QuillScribe Team",
    "--product-name=QuillScribe",
    "--file-version=1.0.0.0",
    "--product-version=1.0.0",
    "--file-description=Beautiful Voice-to-Text Transcription App",
    "--assume-yes-for-downloads",  # Auto-download MinGW64
    "run.py"
)

python @nuitkaArgs

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to build executable with Nuitka" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Verify the executable was created (in --onefile mode, it's in the current directory)
Write-Host "Verifying executable..." -ForegroundColor Yellow
if (-not (Test-Path "QuillScribe.exe")) {
    Write-Host "ERROR: QuillScribe.exe not found in current directory" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Executable built successfully!" -ForegroundColor Green

# Function to find NSIS makensis executable
function Get-MakensisPath {
    # First check if makensis is in PATH
    if (Test-CommandExists "makensis") {
        return "makensis"
    }
    
    # Check common NSIS installation directories
    $nsisLocations = @(
        "C:\Program Files (x86)\NSIS\makensis.exe",
        "C:\Program Files\NSIS\makensis.exe",
        "${env:ProgramFiles(x86)}\NSIS\makensis.exe",
        "$env:ProgramFiles\NSIS\makensis.exe"
    )
    
    foreach ($location in $nsisLocations) {
        if (Test-Path $location) {
            Write-Host "Found NSIS at: $location" -ForegroundColor Green
            return $location
        }
    }
    
    return $null
}

# Check if NSIS is available
$makensisPath = Get-MakensisPath
if ($null -eq $makensisPath) {
    Write-Host ""
    Write-Host "WARNING: NSIS (makensis) not found" -ForegroundColor Yellow
    Write-Host "Skipping installer creation. You can run QuillScribe.exe directly." -ForegroundColor Yellow
    Write-Host "To create an installer, install NSIS from https://nsis.sourceforge.io/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "=========================================" -ForegroundColor Green
    Write-Host "  BUILD COMPLETED!" -ForegroundColor Green
    Write-Host "=========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Executable location: QuillScribe.exe" -ForegroundColor Cyan
    Write-Host ""
    $runExe = Read-Host "Do you want to run QuillScribe.exe now? (y/n)"
    if ($runExe -eq "y" -or $runExe -eq "Y") {
        Start-Process ".\QuillScribe.exe"
    }
    Read-Host "Press Enter to exit"
    exit 0
}

# Create the installer
Write-Host "Creating NSIS installer..." -ForegroundColor Yellow
& $makensisPath installer.nsi
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create installer" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "  BUILD COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Executable location: QuillScribe.exe" -ForegroundColor Cyan
Write-Host "Installer location: QuillScribe-Installer.exe" -ForegroundColor Cyan
Write-Host ""

# Option to run the installer
$runInstaller = Read-Host "Do you want to run the installer now? (y/n)"
if ($runInstaller -eq "y" -or $runInstaller -eq "Y") {
    Start-Process ".\QuillScribe-Installer.exe"
}

Read-Host "Press Enter to exit"

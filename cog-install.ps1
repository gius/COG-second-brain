<#
    COG family install - run once per machine.

        irm https://raw.githubusercontent.com/gius/COG-second-brain/feature/custom-changes/cog-install.ps1 | iex

    Shows the vault folder it intends to use and lets you change it, then installs
    Git and Obsidian (winget), clones the COG vault there, and drops the four
    community plugins in. Safe to re-run: every step skips work already done.

    Set COG_VAULT_PATH beforehand to preseed a different target folder.

    What it deliberately does NOT do: paste the Gemini API key, or set the plugin
    state folder. Both are per-person and take ten seconds in the Obsidian UI.
#>

$ErrorActionPreference = 'Stop'
# Windows PowerShell 5.1 can still default to TLS 1.0, which GitHub refuses.
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
# Invoke-WebRequest's progress bar costs more time than the download itself.
$ProgressPreference = 'SilentlyContinue'

$Repo   = 'https://github.com/gius/COG-second-brain.git'
$Branch = 'feature/custom-changes'
# The git database always lives outside OneDrive, whatever the vault path:
# OneDrive syncing git's internal files is slow and corrupts the repo.
$GitDirParent = Join-Path $env:USERPROFILE '.cog-git'
$GitDir       = Join-Path $GitDirParent 'cog.git'

$Plugins = @(
    @{ Id = 'gemini-scribe';         Repo = 'allenhutchison/obsidian-gemini';        Name = 'Gemini Scribe' }
    @{ Id = 'obsidian-tasks-plugin'; Repo = 'obsidian-tasks-group/obsidian-tasks';   Name = 'Tasks' }
    @{ Id = 'calendar';              Repo = 'liamcain/obsidian-calendar-plugin';     Name = 'Calendar' }
    @{ Id = 'dataview';              Repo = 'blacksmithgu/obsidian-dataview';        Name = 'Dataview' }
)
# No sync plugin here on purpose. The desktop vault is synced by the OneDrive
# client itself; a second syncer pointed at the same folder only adds conflicts.
# Phones need one (OneDrive Sync) and install it by hand - see BFU-SETUP.md.

function Write-Step($Message) { Write-Host "`n== $Message" -ForegroundColor Cyan }
function Write-Skip($Message) { Write-Host "   skipped - $Message" -ForegroundColor DarkGray }

# ── Where the vault goes ────────────────────────────────────────────
# Personal OneDrive is the right home: the desktop client syncs it, and the mobile
# sync plugin only supports the consumer tier. Set COG_VAULT_PATH to preseed a
# different target.

function Get-DefaultVaultPath {
    if ($env:COG_VAULT_PATH) { return $env:COG_VAULT_PATH }
    $Root = if ($env:OneDriveConsumer) { $env:OneDriveConsumer }
            elseif ($env:OneDrive)     { $env:OneDrive }
            else                       { $env:USERPROFILE }
    return (Join-Path $Root 'cog-second-brain')
}

function Test-UnderPath($Path, $Parent) {
    if (-not $Parent) { return $false }
    return $Path.TrimEnd('\').StartsWith($Parent.TrimEnd('\'), [StringComparison]::OrdinalIgnoreCase)
}

# Returns @{ Level = 'block'|'warn'|'info'; Text = '...' } for everything worth
# saying about a candidate path. Blockers make the path unusable.
function Get-PathIssues($Path) {
    $Issues = @()

    # Older Windows sets only OneDrive; newer adds OneDriveConsumer/OneDriveCommercial.
    $PersonalRoots = @($env:OneDriveConsumer)
    if ($env:OneDrive -and $env:OneDrive -ne $env:OneDriveCommercial) { $PersonalRoots += $env:OneDrive }
    $UnderPersonal = @($PersonalRoots | Where-Object { Test-UnderPath $Path $_ }).Count -gt 0

    if (Test-UnderPath $Path $env:OneDriveCommercial) {
        $Issues += @{ Level = 'warn'; Text = 'this is OneDrive for Business - the mobile sync plugin does not support it' }
    } elseif (-not $UnderPersonal) {
        $Issues += @{ Level = 'warn'; Text = 'not inside personal OneDrive - no sync to the phone or to other PCs' }
    }

    $Parent = Split-Path $Path -Parent
    if (-not $Parent) {
        $Issues += @{ Level = 'block'; Text = 'that is not a full path - give something like C:\Users\you\OneDrive\cog-second-brain' }
    } elseif (-not (Test-Path $Parent)) {
        $Issues += @{ Level = 'block'; Text = "the folder above it does not exist: $Parent" }
    }

    if (Test-Path $Path) {
        if (Test-Path (Join-Path $Path '.git')) {
            $Issues += @{ Level = 'info'; Text = 'a COG vault is already here - it will be kept and reused' }
        } elseif (@(Get-ChildItem -Force -LiteralPath $Path -ErrorAction SilentlyContinue).Count -gt 0) {
            $Issues += @{ Level = 'block'; Text = 'that folder already exists and has files in it - git will refuse to clone there' }
        }
    }

    return $Issues
}

function Confirm-VaultPath {
    $Path = Get-DefaultVaultPath

    while ($true) {
        $Issues   = @(Get-PathIssues $Path)
        $Blockers = @($Issues | Where-Object { $_.Level -eq 'block' })

        Write-Host "`nVault folder:  " -NoNewline
        Write-Host $Path -ForegroundColor White
        foreach ($Issue in $Issues) {
            $Color = switch ($Issue.Level) { 'block' { 'Red' } 'warn' { 'Yellow' } default { 'DarkGray' } }
            Write-Host "   $($Issue.Level) - $($Issue.Text)" -ForegroundColor $Color
        }

        $Prompt = if ($Blockers) {
            'Type a different full path (or "q" to quit)'
        } else {
            'Press Enter to use it, or type a different full path (or "q" to quit)'
        }
        $Answer = (Read-Host "`n$Prompt").Trim().Trim('"')

        if ($Answer -eq '') {
            if (-not $Blockers) { return $Path }
            Write-Host 'That path cannot be used. Pick another one.' -ForegroundColor Red
            continue
        }
        if ($Answer -in @('q', 'Q')) { throw 'Cancelled - nothing was installed.' }

        $Path = [Environment]::ExpandEnvironmentVariables($Answer)
    }
}

# winget writes PATH to the registry, not to the running shell.
function Update-SessionPath {
    $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' +
                [Environment]::GetEnvironmentVariable('Path', 'User')
}

# Catches an install in any scope - per-user, machine-wide, or one this shell
# cannot see on PATH yet.
function Test-WingetPackage($Id) {
    winget list --id $Id --exact --source winget 2>$null | Out-Null
    return ($LASTEXITCODE -eq 0)
}

# Judge the outcome, not the exit code: winget returns non-zero for "already
# installed", which is a success for our purposes.
function Install-WingetPackage($Id, $Name) {
    if (Test-WingetPackage $Id) {
        Write-Skip "$Name already installed"
        return
    }
    winget install --id $Id --exact --source winget `
        --accept-source-agreements --accept-package-agreements
    Update-SessionPath
    if (-not (Test-WingetPackage $Id)) {
        throw "Could not install $Name (winget exit $LASTEXITCODE). Install it by hand and re-run."
    }
}

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    throw 'winget is missing. Install "App Installer" from the Microsoft Store, then re-run.'
}

Update-SessionPath

# Confirm the target before anything is installed, so a wrong answer costs nothing.
Write-Step 'Where the vault goes'
$VaultPath = Confirm-VaultPath

Write-Step 'Git'
Install-WingetPackage 'Git.Git' 'Git'
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'Git is installed but not on PATH in this window. Close PowerShell, open it again, and re-run.'
}

Write-Step 'Obsidian'
Install-WingetPackage 'Obsidian.Obsidian' 'Obsidian'

Write-Step "Vault -> $VaultPath"
if (Test-Path (Join-Path $VaultPath '.git')) {
    Write-Skip 'vault already cloned'
} else {
    New-Item -ItemType Directory -Force $GitDirParent | Out-Null
    git clone -b $Branch $Repo --separate-git-dir="$GitDir" "$VaultPath"
    if ($LASTEXITCODE -ne 0) { throw "git clone failed (exit $LASTEXITCODE)" }
}

Write-Step 'Obsidian plugins'
$Installed = @()
foreach ($Plugin in $Plugins) {
    $Dest = Join-Path $VaultPath ".obsidian\plugins\$($Plugin.Id)"
    New-Item -ItemType Directory -Force $Dest | Out-Null

    $Complete = $true
    foreach ($File in 'main.js', 'manifest.json', 'styles.css') {
        $Url = "https://github.com/$($Plugin.Repo)/releases/latest/download/$File"
        try {
            Invoke-WebRequest -Uri $Url -OutFile (Join-Path $Dest $File) -UseBasicParsing
        } catch {
            # styles.css is optional; a plugin without main.js or manifest.json is broken.
            if ($File -ne 'styles.css') { $Complete = $false }
        }
    }

    if ($Complete) {
        $Installed += $Plugin.Id
        Write-Host "   $($Plugin.Name)"
    } else {
        Write-Host "   $($Plugin.Name) - download incomplete, leaving it off. Install it from" -ForegroundColor Yellow
        Write-Host "     Obsidian: Settings -> Community plugins -> Browse." -ForegroundColor Yellow
    }
}

# An incompletely downloaded plugin is never enabled: Obsidian would fail to load
# it on every start.
$PluginList = Join-Path $VaultPath '.obsidian\community-plugins.json'
$Enabled = @($Installed)
if (Test-Path $PluginList) {
    # Assign before wrapping in @(): Windows PowerShell 5.1's ConvertFrom-Json
    # emits a JSON array as ONE object, so @(cmd | ConvertFrom-Json) yields a
    # single nested element instead of the plugin ids.
    try {
        $Parsed = Get-Content $PluginList -Raw | ConvertFrom-Json
    } catch {
        $Parsed = @()
    }
    $Enabled = @(@($Parsed) + $Enabled | Select-Object -Unique)
}
# WriteAllText, not Set-Content: Windows PowerShell 5.1 would prepend a BOM and
# Obsidian's JSON parser rejects it.
[System.IO.File]::WriteAllText($PluginList, (ConvertTo-Json -InputObject $Enabled))

Write-Step 'Excluding the assistant folder'
# gemini-scribe/ holds chat sessions and the generated skills mirror, not notes.
# Obsidian's "Excluded files" setting hides it from search, graph and unlinked
# mentions, and demotes it in the quick switcher. It stays in the file tree.
$ObsidianDir = Join-Path $VaultPath '.obsidian'
New-Item -ItemType Directory -Force $ObsidianDir | Out-Null

# Merge rather than overwrite: Obsidian owns this file and writes its own
# preferences into it on every run.
function Merge-ObsidianJson($Path, $Updates) {
    $Config = @{}
    if (Test-Path $Path) {
        try {
            $Existing = Get-Content $Path -Raw | ConvertFrom-Json
            foreach ($Property in $Existing.PSObject.Properties) {
                $Config[$Property.Name] = $Property.Value
            }
        } catch {
            # Unreadable config: start clean rather than abort the install.
        }
    }
    foreach ($Key in $Updates.Keys) { $Config[$Key] = $Updates[$Key] }
    [System.IO.File]::WriteAllText($Path, (ConvertTo-Json -InputObject $Config -Depth 10))
}

Merge-ObsidianJson (Join-Path $ObsidianDir 'app.json') @{ userIgnoreFilters = @('gemini-scribe/') }
Write-Host '   gemini-scribe excluded from search, graph and quick switcher'

Write-Host @"

Done. Vault: $VaultPath

Finish in Obsidian (about two minutes):

  1. Open Obsidian -> "Open folder as vault" -> pick the folder above.
  2. Settings -> Community plugins -> "Turn on community plugins" if Obsidian
     asks. The four plugins are already on disk.
  3. Settings -> Gemini Scribe -> General:
       Provider    Google Gemini (cloud)
       API key     paste the key Gusta made for you
       Chat model  gemini-3-flash-preview
  4. Same screen -> "Plugin state folder" -> pick "gemini-scribe".
     Check it worked: open the chat panel and type "/" - you should see
     braindump, daily-brief, weekly-checkin and the rest.
  5. Click the sparkles icon and type: Run onboarding

Do not click "Initialize vault context" - it overwrites the tuned COG version.
Full guide: BFU-SETUP.md in the vault folder.
"@ -ForegroundColor Green

param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$mainRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..')).TrimEnd('\')
$auditRoot = Join-Path $mainRoot 'logs/workspace_cleanup_20261007'
$before = Get-Content -LiteralPath (Join-Path $auditRoot 'before.json') -Raw | ConvertFrom-Json
$live = Get-Content -LiteralPath (Join-Path $auditRoot 'live-validation.json') -Raw | ConvertFrom-Json
$targetSet = Get-Content -LiteralPath (Join-Path $auditRoot 'target-set-validation.json') -Raw | ConvertFrom-Json
$receiptPath = Join-Path $mainRoot 'logs/evidence_archives/receipt.json'
$receipt = Get-Content -LiteralPath $receiptPath -Raw | ConvertFrom-Json
$indexPath = Join-Path $mainRoot 'logs/evidence_archives/INDEX.zip'
$indexHash = (Get-FileHash -LiteralPath $indexPath -Algorithm SHA256).Hash.ToLowerInvariant()
if (-not $receipt.crc_all_parts -or -not $receipt.sha256_all_chunks_and_files -or -not $live.all_sha256_match -or $live.index_sha256 -ne $indexHash) {
    throw 'Verified archive and live-file validation are required.'
}
if (-not $targetSet.complete_target_set_match -or $targetSet.index_sha256 -ne $indexHash) {
    throw 'There may be newly created files in the deletion targets; retain targets.'
}
foreach ($property in $receipt.archives.PSObject.Properties) {
    $partPath = Join-Path (Split-Path -Parent $indexPath) $property.Name
    $partHash = (Get-FileHash -LiteralPath $partPath -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($partHash -ne $property.Value.sha256) { throw ('Archive changed after verification: ' + $partPath) }
}
$targets = @($before.targets)
foreach ($target in $targets) {
    $absolute = [IO.Path]::GetFullPath((Join-Path $mainRoot $target.path))
    if ($absolute -ne $target.absolute -or -not $absolute.StartsWith($mainRoot + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw ('Target is outside main workspace: ' + $absolute)
    }
    # Check every parent for a link before recursive operations.
    $walk = $absolute
    while ($walk -ne $mainRoot) {
        if (Test-Path -LiteralPath $walk) {
            $entry = Get-Item -LiteralPath $walk -Force
            if ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw ('Reparse target: ' + $walk) }
        }
        $walk = Split-Path -Parent $walk
    }
}
if (-not $Apply) {
    Write-Output ('Verified targets: ' + $targets.Count)
    Write-Output ('Archived logical GiB: ' + [math]::Round($before.selected_bytes / 1GB, 3))
    Write-Output 'Dry run complete; no files removed.'
    return
}

# No external development or simulator process may be using these targets.
$processes = Get-CimInstance Win32_Process | Where-Object {
    $_.ProcessId -ne $PID -and $_.CommandLine -and $_.CommandLine.Contains($mainRoot) -and
    $_.Name -match '^(example|cserver|cmake|ctest|g\+\+|gcc|cc1plus)\.exe$'
}
if ($processes) { throw 'A build or simulator process still uses the workspace; retain targets.' }

Push-Location $mainRoot
try {
    # `set` enables worktree-specific configuration directly. A preceding init
    # would temporarily exclude every source directory and rewrite retained
    # files on re-checkout, possibly changing their CRLF/LF byte representation.
    $patterns = @('/*') + @($targets | ForEach-Object { '!/' + $_.path + '/' })
    $patterns | & git sparse-checkout set --no-cone --stdin
    if ($LASTEXITCODE -ne 0) { throw 'Sparse apply failed; retain residual files.' }
    $deleted = @()
    # Git has removed only tracked files; archived ignored/untracked residuals
    # are handled explicitly within the checked absolute targets.
    foreach ($target in $targets) {
        $absolute = [IO.Path]::GetFullPath((Join-Path $mainRoot $target.path))
        if (-not $absolute.StartsWith($mainRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe target.' }
        if (Test-Path -LiteralPath $absolute) {
            $entry = Get-Item -LiteralPath $absolute -Force
            if ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Target became a link.' }
            Remove-Item -LiteralPath ('\\?\' + $absolute) -Recurse -Force
        }
        $deleted += $target.path
    }
    [pscustomobject]@{sparse = $true; targets_removed = $deleted; index_sha256 = $indexHash; utc = [DateTime]::UtcNow.ToString('o')} |
        ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $auditRoot 'applied.json') -Encoding utf8
    Write-Output ('Removed verified targets: ' + $deleted.Count)
} finally { Pop-Location }

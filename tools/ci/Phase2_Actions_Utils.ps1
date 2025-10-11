param(
  [switch]$Check,
  [switch]$ProveGate,
  [switch]$RevertGate
)

$ErrorActionPreference = 'Stop'
function NowKST { Get-Date -Format 'yyyy-MM-dd HH:mm:ss K' }

# Paths
$REPO    = 'D:\Endeavour_Dev'
$CI_DIR  = Join-Path $REPO 'tools\ci'
$CF201   = Join-Path $CI_DIR 'cf_201.py'
$OUT_DIR = Join-Path $REPO 'audit_actions'
New-Item -ItemType Directory -Force -Path $OUT_DIR | Out-Null

function Require-Git {
  if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'git not found'
  }
}

function Check-Actions {
  $ts = NowKST
  $report = Join-Path $OUT_DIR ('actions_check_report_{0}.md' -f (Get-Date -Format 'yyyyMMdd_HHmmss'))

  $origin = git -C $REPO remote get-url origin 2>$null
  if ($origin -match '[:/](?<org>[^/]+)/(?<name>[^/.]+)(?:\.git)?$') {
    $ownerRepo = '{0}/{1}' -f $Matches.org,$Matches.name
  } else {
    $ownerRepo = 'fleet1735/Endeavour'
  }

  $lines = @('# Actions Quick Report','','*generated_at*: ' + $ts,'*repo*: ' + $ownerRepo,'')
  if (Get-Command gh -ErrorAction SilentlyContinue) {
    try {
      $runs = gh run list --limit 1 --branch main --json databaseId,headSha,headBranch,status,conclusion,createdAt,updatedAt,displayTitle 2>$null | ConvertFrom-Json
      if ($runs -and $runs.Count -ge 1) {
        $r = $runs[0]
        $lines += '## Latest Run'
        $lines += ('- id: {0}' -f $r.databaseId)
        $lines += ('- title: {0}' -f $r.displayTitle)
        $lines += ('- status/conclusion: {0}/{1}' -f $r.status,$r.conclusion)
        $lines += ('- branch/sha: {0}/{1}' -f $r.headBranch,$r.headSha)
        $lines += ('- created/updated: {0} / {1}' -f $r.createdAt,$r.updatedAt)
        $detail = gh run view $r.databaseId --json jobs,artifacts,conclusion 2>$null | ConvertFrom-Json
        if ($detail) {
          $lines += ''
          $lines += '### Jobs'
          foreach($j in $detail.jobs){ $lines += ('- {0}: {1}' -f $j.name,$j.conclusion) }
          $lines += ''
          $lines += '### Artifacts'
          if ($detail.artifacts) {
            foreach($a in $detail.artifacts){ $lines += ('- {0} ({1} bytes)' -f $a.name,$a.sizeInBytes) }
          } else { $lines += '- (none)' }
          $local = (Get-Content -Raw -ErrorAction SilentlyContinue (Join-Path $REPO 'artifacts\summary_line.txt'))
          if ($local) { $lines += ''; $lines += ('**summary.pass(local-cache)**: ' + ($local -replace '.*=')) }
        }
      } else {
        $lines += '_No runs found on branch main via gh CLI._'
      }
    } catch {
      $lines += ('_gh CLI error: ' + $_.Exception.Message + '_')
    }
  } else {
    $actionsUrl = ('https://github.com/{0}/actions?query=branch%3Amain' -f $ownerRepo)
    try { Start-Process $actionsUrl } catch {}
    $lines += '_gh CLI not installed: opened Actions page in browser._'
    $lines += ('- Opened: ' + $actionsUrl)
  }
  $lines | Set-Content -Encoding utf8 -Path $report
  Write-Host ('Actions report: ' + $report)
}

function Prove-GateFail {
  Require-Git
  if (-not (Test-Path $CF201)) { throw ('not found: ' + $CF201) }
  $bak = ('{0}.bak_{1}' -f $CF201,(Get-Date -Format 'yyyyMMdd_HHmmss'))
  Copy-Item $CF201 $bak -Force
  $raw = Get-Content $CF201 -Raw -Encoding UTF8
  if ($raw -match 'return 2\s*$') {
    Write-Host '[skip] already forced fail'
  } else {
    $patched = $raw -replace 'return 0 if ok else 2','return 2'
    if ($patched -eq $raw) {
      $patched = $raw -replace 'if __name__ == "__main__":\s*sys\.exit\(main\(\)\)','if __name__ == "__main__":`n    sys.exit(2)'
    }
    $patched | Set-Content -Encoding utf8 -Path $CF201
    Write-Host 'cf_201.py patched to fail'
  }
  git -C $REPO add $CF201
  git -C $REPO commit -m 'test(ci): force cf_201 fail to prove gate'
  git -C $REPO push
  Write-Host 'pushed: expect gate FAIL in Actions'
}

function Revert-GateFail {
  Require-Git
  $lastBak = Get-ChildItem ('{0}.bak_*' -f $CF201) -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
  if ($lastBak) {
    Copy-Item $lastBak.FullName $CF201 -Force
    Write-Host ('restored from: ' + $lastBak.Name)
  } else {
    git -C $REPO revert --no-edit HEAD
  }
  git -C $REPO add $CF201
  git -C $REPO commit -m 'revert(ci): restore cf_201 normal exit' 2>$null | Out-Null
  git -C $REPO push
  Write-Host 'pushed: gate PASS path restored'
}

if ($Check)      { Check-Actions;      exit 0 }
if ($ProveGate)  { Prove-GateFail;     exit 0 }
if ($RevertGate) { Revert-GateFail;    exit 0 }
Write-Host 'Usage: .\tools\ci\Phase2_Actions_Utils.ps1 -Check | -ProveGate | -RevertGate'
exit 0



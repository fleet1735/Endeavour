# =========================================================
# Reflex Self-Heal v2.1 (JK 전무님 전용, 엔진 표준판)
# 작성일: 2025-10-10 / PowerShell 7.5+
# =========================================================

function Invoke-Reflex {
    param(
        [string]$ScriptPath,
        [int]$MaxRetry = 3
    )

    Write-Host "`n🚀 Reflex 실행 시작: $ScriptPath"

    if (!(Test-Path $ScriptPath)) {
        Write-Host "⚠️ 파일 없음: $ScriptPath"
        return
    }

    try {
        & $ScriptPath
        Write-Host "✅ 정상 실행 완료 — 오류 없음"
    } catch {
        $err = $_.Exception.Message
        Write-Host "❌ 오류 감지: $err"

        if ($MaxRetry -le 0) {
            Write-Host "🛑 복구 실패 — 최대 재시도 횟수 초과"
            return
        }

        switch -Regex ($err) {

            # ① 함수 매개변수 누락 + 괄호 오류
            "Missing '\)' in function parameter list" {
                Write-Host "🔧 자동 수정: 괄호 누락 및 변수명 누락 패턴 감지"
                $raw = Get-Content $ScriptPath -Raw
                $fixed = $raw -replace '\[string\]\s*,', '[string]$arg1)'
                $fixed = $fixed -replace '\[string\]\s*\)', '[string]$arg1)'
                $fixed | Set-Content $ScriptPath -Encoding UTF8
                Write-Host "🔁 재시도 중..."
                Invoke-Reflex -ScriptPath $ScriptPath -MaxRetry ($MaxRetry - 1)
            }

            # ② BOM·인코딩 관련 오류
            "Unicode escape sequence" {
                Write-Host "🔧 자동 수정: 잘못된 유니코드 시퀀스 제거"
                (Get-Content $ScriptPath -Raw) -replace "``uFEFF","" | Set-Content $ScriptPath -Encoding UTF8
                Write-Host "🔁 재시도 중..."
                Invoke-Reflex -ScriptPath $ScriptPath -MaxRetry ($MaxRetry - 1)
            }

            # ③ 기타 미확인 오류
            default {
                Write-Host "⚠️ 미확인 오류 — 사용자 검토 필요"
            }
        }
    }
}

# =========================================================
# 저장 경로: D:\Endeavour_Dev\agents\reflex\invoke_reflex_v2.1.ps1
# =========================================================

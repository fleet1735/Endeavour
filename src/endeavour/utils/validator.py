import datetime

def validate_signal(signal):
    """
    신호 검증 함수 (Edge Case 5종 포함)
    """
    errors = []

    # Case 1: 가격/시그널 동시 업데이트 충돌
    if signal.get("price_update_time") == signal.get("signal_time"):
        errors.append("CF-101: Price and Signal updated simultaneously - risk of race condition")

    # Case 2: 시장 데이터 지연
    if signal.get("data_delay_ms", 0) > 3000:
        errors.append("CF-102: Market data latency exceeds threshold")

    # Case 3: 신호 신뢰도 하락
    if signal.get("confidence_score", 1) < 0.3:
        errors.append("CF-103: Low confidence signal detected")

    # Case 4: 중복 신호 (최근 5초 내 동일 ID 발생)
    if "recent_signals" in signal:
        now = datetime.datetime.now()
        for prev in signal["recent_signals"]:
            if prev["id"] == signal["id"] and (now - prev["timestamp"]).seconds < 5:
                errors.append("CF-104: Duplicate signal within 5s window")

    # Case 5: 오버라이드 플래그 + 무효 신호
    if signal.get("override_flag") and signal.get("confidence_score", 1) < 0.1:
        errors.append("CF-105: Invalid override on low-confidence signal")

    if not errors:
        return {"status": "OK"}
    else:
        return {"status": "FAIL", "errors": errors}

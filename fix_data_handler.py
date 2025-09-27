from pathlib import Path
from datetime import datetime

# data_handler.py 경로
dh_path = Path("src/endeavour/utils/data_handler.py")

# 백업
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = dh_path.with_suffix(f".py.{ts}.bak")
backup.write_text(dh_path.read_text(encoding="utf-8"), encoding="utf-8")

# 원본 읽기
code = dh_path.read_text(encoding="utf-8").splitlines()

fixed_lines = []
for line in code:
    if line.strip().startswith("need ="):
        # 컬럼 정의 정확히 교정
        fixed_lines.append('    need = {"구분","순위","종목명","Ticker"}')
    elif "VERSION" in line:
        # VERSION 라인 갱신
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        fixed_lines.append(f'VERSION = "data_handler v1.5 | {stamp} KST"')
    else:
        fixed_lines.append(line)

# 저장 (UTF-8)
dh_path.write_text("\n".join(fixed_lines) + "\n", encoding="utf-8")

print(">>> data_handler.py 복구 완료")
print(">>> 백업:", backup)

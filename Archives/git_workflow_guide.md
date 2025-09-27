
# 📘 Git 프로젝트 초기 세팅 & 커밋 워크플로우 정리

## 1. 🔧 프로젝트 초기화

```bash
git init
```
- 로컬 디렉토리를 Git 저장소로 초기화

```bash
git remote add origin https://github.com/fleet1735/Endeavour.git
```
- GitHub 원격 저장소(origin) 등록

---

## 2. 📂 프로젝트 폴더 구성 예시

```plaintext
Endeavour/
├── .git/                ← Git 내부 관리 폴더 (자동 생성됨)
├── .vscode/             ← VS Code 설정
├── archives/            ← 참고자료, 외부문서 등 보관
├── docs/                ← 문서(IPD, change_log 등)
├── reports/             ← 백테스트/최적화 결과
├── src/                 ← 실제 소스 코드 및 전략
│   ├── strategies/
│   └── main.py
└── README.md            ← 프로젝트 설명문서
```

---

## 3. 📝 커밋 및 푸시

### ✅ 변경 사항 반영하기

```bash
git add .
git commit -m "Initial commit with project structure and base files"
```

- 모든 변경 파일(stage)에 추가 후, 커밋

### ✅ GitHub 원격 저장소에 푸시

```bash
git push -u origin main
```

- `main` 브랜치를 `origin`에 push하고 추적 연결(-u)

> 🧨 `! [rejected] main -> main (fetch first)` 오류 시:  
> ```bash
> git pull origin main --rebase  # 또는
> git push -u origin main --force
> ```

---

## 4. 📋 상태 확인 명령어 모음

```bash
git status         # 현재 작업 상태 확인
git branch -vv     # 로컬/원격 브랜치 추적 상태 확인
git remote -v      # 원격 저장소 연결 상태 확인
git log --oneline  # 최근 커밋 로그 간단히 확인
```

---

## 5. 🔄 Git VS Code와 터미널 중 어디서 할까?

- **VS Code GUI**
  - 직관적, 커밋 메시지 작성 편리
  - 하지만 간혹 버벅이거나 삑사리 날 수 있음

- **CMD / 터미널**
  - 안정적이고 에러 대응이 용이함
  - 모든 명령어 직접 입력

> ✅ **추천**: _터미널 기반 작업을 기본으로 하고, VS Code는 시각적 확인용 서브 도구로 활용_

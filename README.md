# Process Scheduling Simulator

Python 3.10 기반의 프로세스 스케줄링 시뮬레이터입니다. FCFS, RR, SPN, SRTN, HRRN, Custom(EAPB)를 지원하고, P/E 코어 처리량 차이와 전력 소비를 함께 계산합니다.

## 실행

```bash
conda create -n os_assign python==3.10 -y
conda activate os_assign
pip install -r requirements.txt
python main.py
```

개발용 바로 실행 스크립트는 macOS/Linux의 `run.sh`, Windows의 `run.bat`입니다.

## 배포용 설치 마법사 만들기

최종 사용자 PC에는 Python이나 패키지를 설치할 필요가 없도록 PyInstaller로 앱을 묶습니다. 단, 배포 파일을 만드는 빌드 PC에는 Python 3.10.8 이상이 필요하며 Python 3.12를 권장합니다. Windows 설치 파일은 Windows에서, macOS 설치 파일은 macOS에서 각각 빌드해야 합니다.

### Windows

```bat
build_windows.bat
```

- Inno Setup이 설치되어 있으면 `release/SchedulerSimulatorSetup.exe`가 생성됩니다.
- Inno Setup이 없으면 `dist/SchedulerSimulator/SchedulerSimulator.exe`와 실행 폴더가 생성됩니다.
- `SchedulerSimulatorSetup.exe`를 다른 Windows PC에서 실행하면 설치 마법사가 열리고, 설치 후 시작 메뉴/선택 시 바탕화면 바로가기로 실행할 수 있습니다.

### macOS

```bash
chmod +x build_macos.sh
./build_macos.sh
```

- `release/SchedulerSimulator.pkg` 설치 마법사가 생성됩니다.
- `release/SchedulerSimulator-mac.dmg`도 함께 생성됩니다.
- `.pkg`를 다른 Mac에서 실행하면 `/Applications/SchedulerSimulator.app`으로 설치되고, 앱 아이콘을 눌러 실행할 수 있습니다.
- `build` 또는 `.pyinstaller-build` 안의 `.pkg`는 PyInstaller 중간 파일이므로 실행하지 않습니다.

서명되지 않은 앱이므로 Windows SmartScreen 또는 macOS Gatekeeper 경고가 나올 수 있습니다. 배포용으로 공개할 때는 코드 서명과 notarization을 추가하는 것이 좋습니다.

## 테스트

```bash
python -m pytest
```

## 알고리즘

- FCFS: 먼저 도착한 작업을 먼저 실행하는 비선점 방식입니다.
- RR: tick 단위 Time-quantum `δ`를 사용하는 선점 방식입니다. P 코어에서도 `δ`는 work unit이 아니라 tick으로 계산합니다.
- SPN: idle 코어가 생길 때 burst time이 가장 짧은 작업을 고르는 비선점 방식입니다.
- SRTN: 매 tick remaining이 가장 짧은 작업을 고르는 선점 방식입니다.
- HRRN: response ratio `(waiting_time + burst_time) / burst_time`가 가장 높은 작업을 고르는 비선점 방식입니다.
- Custom: EAPB(Energy-Aware P-core Boost)입니다. 정규화된 HRRN 우선순위와 EDP 기반 P/E 코어 선택을 결합한 자체 휴리스틱입니다.

## 구현 가정

- tick 단위는 1초입니다.
- arrival time이 현재 tick과 같으면 즉시 실행 후보가 됩니다.
- 완료 시각은 마지막으로 실행된 tick의 다음 시각입니다.
- Ready queue는 모든 코어가 공유합니다.
- 기존 실행 작업은 같은 코어에서 계속 실행하는 것을 우선합니다.
- 신규 배정은 E 코어를 P 코어보다 우선합니다.
- idle에서 active로 전환될 때만 startup power를 부과합니다.
- P 코어는 tick당 2 work units를 처리하지만, 남은 일이 1이어도 1 tick의 active power를 소비합니다.

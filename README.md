# Process Scheduling Simulator

Python 3.10 기반의 프로세스 스케줄링 시뮬레이터입니다. FCFS, RR, SPN, SRTN, HRRN, Custom placeholder를 지원하고, P/E 코어 처리량 차이와 전력 소비를 함께 계산합니다.

## 실행

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Windows에서는 다음 명령을 사용할 수 있습니다.

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

개발용 바로 실행 스크립트는 macOS/Linux의 `run.sh`, Windows의 `run.bat`입니다.

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
- Custom: 현재는 FCFS fallback입니다. 자체 알고리즘을 이후에 교체할 수 있도록 인터페이스만 확보했습니다.

## 구현 가정

- tick 단위는 1초입니다.
- arrival time이 현재 tick과 같으면 즉시 실행 후보가 됩니다.
- 완료 시각은 마지막으로 실행된 tick의 다음 시각입니다.
- Ready queue는 모든 코어가 공유합니다.
- 기존 실행 작업은 같은 코어에서 계속 실행하는 것을 우선합니다.
- 신규 배정은 E 코어를 P 코어보다 우선합니다.
- idle에서 active로 전환될 때만 startup power를 부과합니다.
- P 코어는 tick당 2 work units를 처리하지만, 남은 일이 1이어도 1 tick의 active power를 소비합니다.# OS_scheduler_simulator
# OS_scheduler_simulator

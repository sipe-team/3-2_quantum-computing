import cirq
import numpy as np
from fractions import Fraction

    
def find_period(a: int, N: int) -> int:
    # N을 표현하는 데 필요한 비트 수 계산
    # N을 이진수로 변환: bin(15) = '0b1111'
    # n_count = 4 (이진수 1111의 길이)
    n_count = len(bin(N)[2:])
    
    # 정확도를 높이기 위해 추가 정밀도를 위한 큐비트 수 설정
    # precision_qubits = 2 * 4 + 3 = 11
    precision_qubits = 2 * n_count + 3
    
    # 큐비트 생성: 계수 큐비트와 보조 큐비트
    # counting_qubits = [(0,0), (0,1), (0,2), ..., (0,10)] 11개 생성
    counting_qubits = [cirq.GridQubit(0, i) for i in range(precision_qubits)]
    # auxiliary_qubit = (1,0) 1개 생성
    auxiliary_qubit = cirq.GridQubit(1, 0)
    
    # 양자 회로 생성
    circuit = cirq.Circuit()
    
    # 계수 큐비트를 중첩(superposition) 상태로 초기화
    circuit.append(cirq.H.on_each(counting_qubits))
    
    # 보조 큐비트를 |1⟩ 상태로 초기화
    circuit.append(cirq.X(auxiliary_qubit))
    
    # 제어된 U 연산 적용
    for i, counting_qubit in enumerate(counting_qubits):
        # U 연산의 지수를 계산 (a^(2^i) mod N)
        # 예시: a=7일 때의 각 power 값
        # i=0: power = 7^1 mod 15 = 7
        # i=1: power = 7^2 mod 15 = 4
        # i=2: power = 7^4 mod 15 = 1
        # i=3: power = 7^8 mod 15 = 1
        # ...
        power = pow(a, 2**i, N)
        
        # 제어된 U 연산 생성
        controlled_U = cirq.ControlledOperation(
            [counting_qubit],
            cirq.MatrixGate(cirq.unitary(cirq.X) ** power).on(auxiliary_qubit)
        )
        
        # 회로에 제어된 U 연산 추가
        circuit.append(controlled_U)
    
    # 계수 큐비트에 역 양자 퓨리에 변환(QFT) 적용
    circuit.append(cirq.qft(*counting_qubits, inverse=True))
    
    # 계수 큐비트 측정
    circuit.append(cirq.measure(*counting_qubits, key='result'))
    
    # 양자 회로 시뮬레이션
    simulator = cirq.Simulator()
    result = simulator.run(circuit, repetitions=1)
    
    # 측정 결과 처리
    # 예시 measurements = [0,1,0,0,1,1,0,0,0,1,0]
    measurements = result.measurements['result'][0]
    # 측정값을 이진수로부터 정수로 변환 (예: 314)
    measurement = sum([bit * (2 ** i) for i, bit in enumerate(reversed(measurements))])
    
    # 측정값을 사용하여 주기 계산
    # 측정값을 분수로 변환 (예: 314/2048 ≈ 1/4)
    # 분모를 주기로 사용 (period = 4)
    fraction = Fraction(measurement, 2 ** precision_qubits).limit_denominator(N)
    period = fraction.denominator
    
    return period


def shor_algorithm(N: int, max_attempts: int = 5):
    # N=15는 짝수가 아니므로 이 조건은 스킵
    if N % 2 == 0:
        return 2
    
    # 5번 시도
    for _ in range(max_attempts):
        # coprime한 a 선택
        # 예시: a=7 선택
        a = np.random.randint(2, N) # 2부터 14 사이의 난수 생성
        
        # gcd(7,15) = 1이므로 계속 진행
        if np.gcd(a, N) != 1:
            return np.gcd(a, N)
        
        try:
            # period = 4 반환
            period = find_period(a, N)
            if period is None:
                continue
            
            # period = 4는 짝수이므로 다음 단계 진행
            if period % 2 == 0:
                # candidate = 7^2 mod 15 = 4
                candidate = pow(a, period // 2, N)
                if candidate != N - 1: # 4 != 14
                    # factor1 = gcd(5,15) = 5
                    factor1 = np.gcd(candidate + 1, N)
                    # factor2 = gcd(3,15) = 3
                    factor2 = np.gcd(candidate - 1, N)
                    if factor1 > 1:
                        return factor1 # 5 반환
                    if factor2 > 1:
                        return factor2 # 3 반환
        except Exception as e:
            print(f"Attempt failed: {e}")
            continue
            
    return None
N = 15
max_attempts = 5
# factor = 3 또는 5 반환
factor = shor_algorithm(N, max_attempts)
if factor:
    print(f"Found factor of {N}: {factor}")
    other_factor = N // factor
    print(f"Complete factorization: {factor} × {other_factor}")
else:
    print("No factor found")

import cirq
import numpy as np
from fractions import Fraction

    
def find_period(a: int, N: int) -> int:
    # N을 표현하는 데 필요한 비트 수 계산
    n_count = len(bin(N)[2:])
    
    # 정확도를 높이기 위해 추가 정밀도를 위한 큐비트 수 설정
    precision_qubits = 2 * n_count + 3
    
    # 큐비트 생성: 계수 큐비트와 보조 큐비트
    counting_qubits = [cirq.GridQubit(0, i) for i in range(precision_qubits)]
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
    measurements = result.measurements['result'][0]
    # 측정값을 이진수로부터 정수로 변환
    measurement = sum([bit * (2 ** i) for i, bit in enumerate(reversed(measurements))])
    
    # 측정값을 사용하여 주기 계산
    fraction = Fraction(measurement, 2 ** precision_qubits).limit_denominator(N)
    period = fraction.denominator
    
    return period


def shor_algorithm(N: int, max_attempts: int = 5):
    if N % 2 == 0:
        return 2
    
    for _ in range(max_attempts):
        # coprime한 a 선택
        a = np.random.randint(2, N)
        if np.gcd(a, N) != 1:
            return np.gcd(a, N)
        
        try:
            period = find_period(a, N)
            if period is None:
                continue
                
            if period % 2 == 0:
                candidate = pow(a, period // 2, N)
                if candidate != N - 1:
                    factor1 = np.gcd(candidate + 1, N)
                    factor2 = np.gcd(candidate - 1, N)
                    if factor1 > 1:
                        return factor1
                    if factor2 > 1:
                        return factor2
        except Exception as e:
            print(f"Attempt failed: {e}")
            continue
            
    return None
N = 15
max_attempts = 5
factor = shor_algorithm(N, max_attempts)
if factor:
    print(f"Found factor of {N}: {factor}")
    other_factor = N // factor
    print(f"Complete factorization: {factor} × {other_factor}")
else:
    print("No factor found")

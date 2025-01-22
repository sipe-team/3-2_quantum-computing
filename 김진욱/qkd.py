import cirq
import random

# BB84 알고리즘

# 1. Alice의 비트 생성 및 베이스 선택
def alice_prepare_qubits():
    qubits = [cirq.LineQubit(i) for i in range(4)]  # 큐비트 4개 생성
    bits = []
    bases = []
    operations = []
    
    for i in range(4):
        bit = random.choice([0, 1])  # 비트는 0 또는 1
        base = random.choice([0, 1])  # 0: 수평/수직, 1: 대각선
        
        bits.append(bit)
        bases.append(base)
        
        if base == 0:  # 수평/수직 베이스 (수직 / 수평)
            if bit == 1:
                operations.append(cirq.X(qubits[i]))  # X 게이트 (1일 때)
            else:
                operations.append(cirq.I(qubits[i]))  # I 게이트 (0일 때)
        else:  # 대각선 베이스 (대각선 / 대각선 반대)
            if bit == 1:
                operations.append(cirq.H(qubits[i]))  # H 게이트 (1일 때)
            else:
                operations.append(cirq.I(qubits[i]))  # I 게이트 (0일 때)
    
    return qubits, operations, bits, bases

# 2. Bob의 측정 (Bob의 기저도 랜덤하게 생성)
def bob_measure_qubits(qubits, bases):
    measurements = []
    bob_bases = [random.choice([0, 1]) for _ in range(len(bases))]  # Bob의 기저 랜덤 설정
    print(f"Bob's Bases: {bob_bases}")  # Bob의 기저 출력
    
    for i, qubit in enumerate(qubits):
        if bob_bases[i] == 0:  # 수평/수직 베이스
            measurements.append(cirq.measure(qubits[i], key=f'qubit_{i}'))
        else:  # 대각선 베이스
            measurements.append(cirq.H(qubits[i]))  # 대각선 베이스 측정을 위해 H 게이트
            measurements.append(cirq.measure(qubits[i], key=f'qubit_{i}'))
    
    return measurements, bob_bases

# 3. Alice와 Bob의 결과 비교
def compare_results(alice_bits, alice_bases, bob_measurements, bob_bases):
    shared_key = []
    for i in range(len(alice_bits)):
        if alice_bases[i] == bob_bases[i]:
            shared_key.append(bob_measurements[i])
    return shared_key

# 4. 시뮬레이션
def main():
    qubits, operations, alice_bits, alice_bases = alice_prepare_qubits()
    print(f"Alice's Bits: {alice_bits}")
    print(f"Alice's Bases: {alice_bases}")
    
    # Cirq의 Circuit 객체 생성
    circuit = cirq.Circuit(operations)
    
    # Bob의 측정을 포함한 회로 추가
    measurements, bob_bases = bob_measure_qubits(qubits, alice_bases)
    circuit.append(measurements)
    
    # 시뮬레이터 실행
    simulator = cirq.Simulator()
    result = simulator.run(circuit, repetitions=1)
    
    # Bob의 측정 결과 얻기 (배열에서 첫 번째 값 추출)
    bob_measurements = []
    for i in range(4):
        # 배열에서 첫 번째 값만 추출하여 평탄화
        bob_measurements.append(result.measurements[f'qubit_{i}'][0][0])
    
    print(f"Bob's Measured Bits: {bob_measurements}")
    
    # Alice와 Bob이 사용하는 베이스를 비교하여 공유 키를 생성
    shared_key = compare_results(alice_bits, alice_bases, bob_measurements, bob_bases)
    print(f"Shared Key: {shared_key}")

if __name__ == '__main__':
    main()
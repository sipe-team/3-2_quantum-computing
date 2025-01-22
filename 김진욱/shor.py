import cirq
import numpy as np
from math import gcd
import random

# 양자 푸리에 변환 (QFT)
def qft(qubits):
    circuit = cirq.Circuit()
    n = len(qubits)
    for i in range(n):
        for j in range(i):
            circuit.append(cirq.CZPowGate(exponent=1 / (2 ** (i - j))).on(qubits[i], qubits[j]))
        circuit.append(cirq.H.on(qubits[i]))
    return circuit

# inverse QFT
def inverse_qft(qubits):
    circuit = cirq.Circuit()
    n = len(qubits)
    for i in range(n - 1, -1, -1):
        circuit.append(cirq.H.on(qubits[i]))
        for j in range(i - 1, -1, -1):
            circuit.append(cirq.CZPowGate(exponent=-1 / (2 ** (i - j))).on(qubits[i], qubits[j]))
    return circuit

# 모듈러 지수 연산
def modular_exponentiation(a, N, x_qubits, result_qubits):
    circuit = cirq.Circuit()
    n = len(x_qubits)

    for i, qubit in enumerate(x_qubits):
        power = 2**i
        mod_exp_value = (a**power) % N
        for j, result_qubit in enumerate(result_qubits):
            if (mod_exp_value >> j) & 1:
                circuit.append(cirq.ControlledGate(cirq.X).on(qubit, result_qubit))
    return circuit

# 주기 찾기 함수
def find_period(x, N, a):
    for r in range(1, N):
        if pow(a, r, N) == 1:
            # r이 짝수이고, a^(r/2) != -1 mod N 조건 확인
            if r % 2 == 0 and pow(a, r // 2, N) != (N - 1):
                return r
    return None

# 쇼어 알고리즘 실행 함수
def run_shor_with_retries(N, max_retries=5):
    n_qubits = int(np.ceil(np.log2(N)))
    x_register = [cirq.LineQubit(i) for i in range(n_qubits)]
    result_register = [cirq.LineQubit(i + n_qubits) for i in range(n_qubits)]

    for attempt in range(max_retries):
        # 랜덤으로 a 선택 (1 < a < N, gcd(a, N) = 1)
        while True:
            a = random.randint(2, N - 1)
            if gcd(a, N) == 1:
                break

        print(f"Attempt {attempt + 1}: Trying a = {a}")

        circuit = cirq.Circuit()
        circuit.append(cirq.H.on_each(*x_register))
        circuit.append(modular_exponentiation(a, N, x_qubits=x_register, result_qubits=result_register))
        circuit += inverse_qft(x_register)
        circuit.append(cirq.measure(*x_register, key='x'))

        # Run
        simulator = cirq.Simulator()
        result = simulator.run(circuit, repetitions=1)
        measured_x = int("".join(map(str, result.measurements['x'][0][::-1])), 2)

        if measured_x == 0:
            print(f"Attempt {attempt + 1}: Measured x is zero. Retrying...")
            continue

        r = find_period(measured_x, N, a)
        if r is None:
            print(f"Attempt {attempt + 1}: No valid period r found. Retrying...")
            continue

        p = gcd(a**(r // 2) - 1, N)
        q = gcd(a**(r // 2) + 1, N)

        if p * q == N and p != 1 and q != 1:
            return p, q, circuit

        print(f"Attempt {attempt + 1}: Invalid factors p={p}, q={q}. Retrying...")

    raise Exception("maximum retries")

# 실행 예제
if __name__ == "__main__":
    N = 35  # Number to factorize

    try:
        p, q, circuit = run_shor_with_retries(N)
        print(f"Factors of {N} are p={p} and q={q}")
    except Exception as e:
        print(f"Error: {e}")
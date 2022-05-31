# Anisotropic gate error amplification
Library for generating anisotropic gate error amplification sequence automatically

## Usage

When you want to amplify the ZZ-Hamiltonian error in RZX(180) gate, please run the following code: 
```python
from anisotropic_gate_error_amplification import make_echo
echo_str = make_echo(error_str="ZZ", gate_str="ZX")
print(echo_str)
```
Then, you will get as follows:
```
[ZZ, XX, ZZ, IX, ZZ, XX, ZZ, IX]
```
In such case, you should run the gate sequence as follows:
```python
from sequence_parser import Circuit

ansatz = Circuit(backend)
for _ in range(4):
  ansatz.rzx45(control, target)

cir = Circuit(backend)
for _ in range(2*L):
  cir.call(ansatz)
  cir.Z(control)
  cir.Z(target)
  cir.call(ansatz)
  cir.X(control)
  cir.X(target)
  cir.call(ansatz)
  cir.Z(control)
  cir.Z(target)
  cir.call(ansatz)
  cir.I(control)
  cir.X(target)
```
, where L is amplification index.

# Anisotropic gate error amplification
Library for generating anisotropic gate error amplification sequence automatically

## Usage

When you want to amplify the ZZ Hamiltonian error in RZX gate, please run the following code: 
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

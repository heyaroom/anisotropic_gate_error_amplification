import itertools
import numpy as np
import networkx as nx
from .minimum_clique_cover import clique_cover
from .pauli_operator import PauliOperator

def make_n_echo(n):
    x = [2*n-1]
    for i in range(2*n-2):
        x = x + [i+1] + x
    x = x + [i+1]
    return x

def make_echo(error_str:str, gate_str:str):
    if len(error_str) != len(gate_str):
        raise

    n = len(error_str)
    hamiltonian_pauli_error = PauliOperator(error_str)
    target_pauli_gate = PauliOperator(gate_str)

    if hamiltonian_pauli_error.is_commute(target_pauli_gate):
        rotation_error =  hamiltonian_pauli_error
    else:
        rotation_error = hamiltonian_pauli_error*target_pauli_gate

    labels = ["".join(i) for i in itertools.product(["I","X","Y","Z"], repeat=n)]
    paulis = [PauliOperator(i) for i in labels]

    nodes = []
    for pauli in paulis:
        if rotation_error.is_commute(pauli):
            nodes.append(pauli)
            
    edges = []
    for a,b in itertools.product(nodes, repeat=2):
        if a.string != b.string:
            if not a.is_commute(b):
                edges.append((a.string, b.string))
                
    g = nx.Graph()
    g.add_edges_from(edges)

    cliques = clique_cover(g)
    size = [len(clique) for clique in cliques]
    clique = cliques[np.argmax(size)]
    clique.append(rotation_error.string)
    clique = np.array(clique)

    echo = make_n_echo(n)
    sol = clique[echo]

    echo_array = [PauliOperator(i)*target_pauli_gate for i in sol]
    return echo_array
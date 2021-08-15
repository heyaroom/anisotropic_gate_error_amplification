
from collections import defaultdict
import numpy as np
import networkx as nx
import networkx.algorithms.approximation as approx
import networkx.algorithms.coloring as coloring
import pulp

def clique_random_sequential(graph : nx.Graph) -> list:
    """Perform minimum clique cover with random sequential greedy method

    This method will create clique greedily. At least finish with O(|V|^2).

    Args:
        graph (nx.Graph): graph to solve
    Returns:
        list: list of node names for each clique
    """
    graph = graph.copy()
    clique_list = []
    while len(graph.nodes())>0:
        clique = []
        node_list = list(graph.nodes())
        np.random.permutation(node_list)
        for node in node_list:
            flag = True
            for exist_node in clique:
                if node not in graph[exist_node]:
                    flag =False
                    break
            if flag:
                clique.append(node)
        graph.remove_nodes_from(clique)
        clique_list.append(clique)
    return clique_list

def clique_approx_find_greedy_eliminate(graph: nx.Graph) -> list:
    """Perform minimum clique cover by approximatly find maximum clique and iteratively eliminate it.

    Find the maximum clique with approximatino methods and iteratively eliminate it.

    Args:
        graph (nx.Graph): graph to solve
    Returns:
        list: list of node names for each clique
    """
    _, clique_list = approx.clique_removal(graph)
    clique_list = [list(item) for item in clique_list]
    return clique_list

def clique_exact_find_greedy_eliminate(graph: nx.Graph) -> list:
    """Perform minimum clique cover by exactly find maximum clique and iteratively eliminate it.

    Find the maximum clique by enumerating all the cliques and iteratively eliminate it.

    Args:
        graph (nx.Graph): graph to solve
    Returns:
        list: list of node names for each clique
    """
    graph = graph.copy()
    clique_list = []
    while len(graph.nodes())>0:
        max_size = 0
        max_clique = []
        for clique in nx.find_cliques(graph):
            size = len(clique)
            if size > max_size:
                max_size = size
                max_clique = clique
        graph.remove_nodes_from(max_clique)
        clique_list.append(max_clique)
    return clique_list

def clique_exact_find_once_greedy_eliminate(graph: nx.Graph) -> list:
    """Perform minimum clique cover by exactly find maximum clique and iteratively eliminate it.

    Find the maximum clique by enumerating all the cliques once and iteratively eliminate it.

    Args:
        graph (nx.Graph): graph to solve
    Returns:
        list: list of node names for each clique
    """
    max_cliques = sorted(nx.find_cliques(graph), key=lambda x: len(x), reverse=True)
    max_cliques = [set(i) for i in max_cliques]
    clique_list = []
    while np.sum([len(i) for i in max_cliques]) > 0:
        max_clique = max_cliques[0]
        max_cliques = [i - max_clique for i in max_cliques]
        max_cliques = sorted(max_cliques, key=lambda x: len(x), reverse=True)
        clique_list.append(max_clique)
    return clique_list

def coloring_greedy(graph: nx.Graph, strategy: str) -> list:
    """Perform minimum clique cover by reducing problem into coloring problem and using approximation methods.

    See https://networkx.github.io/documentation/stable/reference/algorithms/coloring.html
    for detailed algorithms

    Args:
        graph (nx.Graph): graph to solve
        strategy (str): name of strategy
    Returns:
        list: list of node names for each clique
    """
    graph = nx.complement(graph)
    result = coloring.greedy_color(graph, strategy=strategy)
    clique_dict = defaultdict(list)
    for node,color in result.items():
        clique_dict[color].append(node)
    return list(clique_dict.values())

class AbortedError(Exception):
    pass

def integer_programming(graph: nx.Graph) -> list:
    """Perform minimum clique cover by reducing problem into integer programming.

    If solver says optimal, optimal solution for minimum clique cover is obtained,
    but it may take very long time for large problems.

    TODO: Check installation of commercial IP solvers such as CPLEX, Gurobi, and 
    use them if they are installed.

    Args:
        graph (nx.Graph): graph to solve
    Returns:
        list: list of node names for each clique
    Raises:
        Exception: Solver cannot solve IP problem.
    """
    problem = pulp.LpProblem("clique_cover", pulp.LpMinimize)

    clique_max_count = len(graph.nodes())
    clique_vars = []
    for ind in range(clique_max_count):
        var = pulp.LpVariable("clique{}".format(ind), cat="Binary")
        clique_vars.append(var)

    node_belong_vars = []
    for ind in range(clique_max_count):
        node_belong_vars.append({})
        for node in graph.nodes():
            nodename = str(node)
            nodename = nodename.replace("  ","0").replace(" i","1").replace(" -","2").replace("-i","3")
            var = pulp.LpVariable("{}_{}".format(nodename,ind), cat = "Binary")
            node_belong_vars[ind][node] = var
    
    # minimize used cliques
    problem += sum(clique_vars)

    # if node belongs, clique must be used
    for ind in range(clique_max_count):
        for node in graph.nodes():
            problem += (node_belong_vars[ind][node] <= clique_vars[ind])

    # clique must be exclusive   
    for node in graph.nodes():
        items = []
        for ind in range(clique_max_count):
            items.append(node_belong_vars[ind][node])
        problem += (sum(items)==1)

    # not-neighboring nodes cannot belong the same clique
    for ind in range(clique_max_count):
        for i1, n1 in enumerate(graph.nodes()):
            for i2, n2 in enumerate(graph.nodes()):
                if i2<=i1: continue
                if n2 not in graph[n1]:
                    problem += (node_belong_vars[ind][n1]+node_belong_vars[ind][n2]<=1)
    
    #status = problem.solve()
    import multiprocessing
    cpu_count = multiprocessing.cpu_count()
    status = problem.solve(pulp.PULP_CBC_CMD(threads=cpu_count, keepFiles=0, mip=1, maxSeconds=5))
    #status = problem.solve(pulp.PULP_CBC_CMD(maxSeconds=5, msg=0, fracGap=0))
    #print(problem)
    #print(pulp.LpStatus[status])
    #print(problem.objective.value())

    # cannot solve
    if status <= 0:
        raise AbortedError("Solver cannot solve problem.")

    clique_dict = defaultdict(list)
    node_count = 0
    for node in graph.nodes():
        for index in range(clique_max_count):
            var = node_belong_vars[index][node]
            if(var.value()>=0.5):
                clique_dict[index].append(node)
                node_count += 1
                break
    return list(clique_dict.values())

strategy_func = {
    "clique_random_sequential" : clique_random_sequential,
    "clique_approx_find_greedy_eliminate" : clique_approx_find_greedy_eliminate,
    "clique_exact_find_greedy_eliminate" : clique_exact_find_greedy_eliminate,
    "clique_exact_find_once_greedy_eliminate" : clique_exact_find_once_greedy_eliminate,
    "coloring_largest_first" : None,
    "coloring_smallest_last" : None,
    "coloring_random_sequential" : None,
    "coloring_independent_set" : None,
    "coloring_connected_sequential_bfs" : None,
    "coloring_connected_sequential_dfs" : None,
    "coloring_saturation_largest_first" : None,
    "integer_programming" : integer_programming,
}

clique_cover_strategies = strategy_func.keys()

def clique_cover(graph: nx.graph, strategy:str ="clique_random_sequential") -> list:
    """Perform minimum clique cover using several strategies

    Args:
        graph (nx.Graph): graph to solve
        strategy (str): name of strategy
    Returns:
        list: list of node names for each clique
    """
    if strategy not in strategy_func:
        raise ValueError("Unknown strategy, choose from {}".format(strategy_func.keys()))

    coloring_prefix = "coloring_"
    if coloring_prefix in strategy:
        return coloring_greedy(graph, strategy = strategy[len(coloring_prefix):])
    return strategy_func[strategy](graph)


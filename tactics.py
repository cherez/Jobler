import copy

def reduce(graph):
    reduced = False
    #keep reducing as long as we make progress
    while reduce_values(graph) or reduce_nodes(graph):
        reduced = True
    return reduced

def reduce_values(graph):
    values = {}
    repeats = {}
    #find every set of equal values that are calculated
    for i in graph.values:
        if not i.ready():
            continue
        if i.value not in values:
            values[i.value] = i
        else:
            repeats[i] = values[i.value]

    #replace all repeats with just one of the values
    for copy, orig in repeats.items():
        graph._merge_values(orig, copy)
    return bool(repeats)

def reduce_nodes(graph):
    remaining = []
    #since we'll be deleting as we go, we need to iterate a copy
    for i in copy.copy(graph.nodes):
        for j in remaining:
            if i == j:
                graph._merge_nodes(j, i)
                break
        else:
            remaining.append(i)
    if len(remaining) != len(graph.nodes):
        graph.nodes[:] = remaining
        return True
    return False

def execute(graph):
    ready = [i for i in graph.nodes if i.ready()]
    if not ready:
        return False
    for i in ready:
            i.execute()
    return True

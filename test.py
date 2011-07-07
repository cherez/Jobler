#!/bin/env python
import graph
import traceback

class Add(graph.Process):
    inputs = ['first', 'second']
    outputs = ['result']
    @staticmethod
    def execute(first, second):
        yield {'result':first+second}

class Multiply(graph.Process):
    inputs = ['first', 'second']
    outputs = ['result']
    @staticmethod
    def execute(first, second):
        yield {'result':first*second}

def test_basics():
    g = graph.Graph()
    a = Add()
    first = graph.Value(1)
    second = graph.Value(2)
    result = graph.Value()
    n = graph.Node(a, {'first':first, 'second':second}, {'result':result})
    g.add_node(n)
    while g.execute():
        pass
    if result.value != 3:
        print('1 + 2 = %s ?' % result.value)
        traceback.print_stack()
        return False
    return True

def test_reduce_values():
    g = graph.Graph()
    m = Multiply()
    first = graph.Value(1)
    second = graph.Value(1)
    result = graph.Value()
    n = graph.Node(m, {'first':first, 'second':second}, {'result':result})
    g.add_node(n)
    g.reduce_values()
    if len(g.values) != 2:
        print('Incorrect number of values after reduce_values. '\
                'Expected 2, got %s' % len(g.values))
        traceback.print_stack()
        return False
    while g.execute():
        pass
    if result.value != 1:
        print('1 * 1 = %s ?' % result.value)
        traceback.print_stack()
        return False
    g.reduce_values()
    if len(g.values) != 1:
        print('Incorrect number of values after reduce_values. ' \
                'Expected 1, got %s' % len(g.values))
        traceback.print_stack()
        return False
    return True

def test_reduce_nodes():
    g = graph.Graph()
    m = Multiply()
    first = graph.Value(1)
    second = graph.Value(1)
    for i in range(4):
        result = graph.Value()
        n = graph.Node(m, {'first':first, 'second':second}, {'result':result})
        g.add_node(n)
    g.reduce_nodes()
    if len(g.nodes) != 1:
        print('Incorrect number of nodes after reduce_nodes. ' \
                'Expected 1, got %s' % len(g.nodes))
        traceback.print_stack()
        return False
    return True

def test_reduce():
    g = graph.Graph()
    m = Multiply()
    for i in range(4):
        first = graph.Value(1)
        second = graph.Value(1)
        result = graph.Value()
        n = graph.Node(m, {'first':first, 'second':second}, {'result':result})
        g.add_node(n)
    g.reduce()
    if len(g.nodes) != 1:
        print('Incorrect number of nodes after reduce. '\
                'Expected 1, got %s' % len(g.nodes))
        traceback.print_stack()
        return False
    if len(g.values) != 2:
        print('Incorrect number of values after reduce. '\
                'Expected 2, got %s' % len(g.values))
        for i in g.values:
            print(i.value, i.depends)
        return False
    while g.execute():
        pass
    return True

def test():
    tests = [
            test_basics,
            test_reduce_values,
            test_reduce_nodes,
            test_reduce
            ]
    successes = 0
    for test in tests:
        if test():
            successes += 1
    print('%s succeeded out of %s' % (successes, len(tests)))

if __name__ == '__main__':
    test()

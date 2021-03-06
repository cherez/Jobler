import types
import traceback

class Value(object):
    def __init__(self, value = None, depends = None):
        self.value = value
        self.depends = depends

    def ready(self):
        if self.depends:
            return self.depends.done() and not self.depends.error()
        return True

class Process(object):
    inputs = [] #Names
    outputs = [] #Names
    result = {}

    def __init__(self):
        pass

  ##This should be a generator, yielding None until finished, then yielding  {Name:value}
    def execute(self, **inputs):
        raise NotImplementedError('Tried to run a basic Process; this method to be overridden in a subclass.')

class Node(object):
    def __init__(self, process = None, inputs = {}, outputs = {}):
        self.process = process
        self.inputs = inputs #Name : Value
        self.outputs = outputs #Name : Value

        self._done = False #Set to true after this runs
        self._running = False
        self._generator = None
        self._error = False

        for i in outputs.values():
            i.depends = self

    def execute(self):
        #perhaps this should be moved into tactics?
        if self._done:
            return True
        if self._error:
            return False
        #if we have a generator, then we've started; poll it to see if it's done
        if self._running:
            try:
                value = next(self._generator)
            except:
                self._error = True
                self._running = False
                raise

            #this means that we're still processing
            if value is None:
                return True

            #otherwise, we're done
            self._generator = None
            self._running = False

            if not isinstance(value, dict):
                self._error = True
                self._running = False
                raise TypeError('Expected Process %s to yield None or a' \
                                'dictionary, got %s.' % (self.process, value))

            vkeys = set(value.keys())
            okeys = set(self.outputs.keys())
            if not okeys <= vkeys:
                self._error = True
                self._running = False
                raise ValueError('Not all expected output values returned by '\
                                  'Process %s. Missing $s.' % \
                                  (self.process, okeys -vkeys))
            for i in okeys:
                self.outputs[i].value = value[i]
            self._done = True
            self.result = value
            return True

        #this means we haven't started yet
        else:
            #check if all our inputs are ready
            if not self.ready():
                return False

            inputs = {}
            for i in self.inputs.keys():
                inputs[i] = self.inputs[i].value
            generator = self.process.execute(**inputs)
            if type(generator) is not types.GeneratorType:
                self._error = True
                raise ValueError('Process %s execution did not return a ' \
                                  'generator; got %s instead.' % \
                                  (self.process, generator))
            self._generator = generator
            self._running = True
            #run the first step of our iterator
            return self.execute()

    def ready(self):
        #this is ready if all its inputs are ready
        return not self._done and not self._error and \
                all(i.ready() for i in self.inputs.values())

    def done(self):
        return self._done

    def error(self):
        return self._error

    def running(self):
        return self._running

    def __eq__(self, other):
        return self.process == other.process and self.inputs == other.inputs

class Graph(object):
    def __init__(self):
        self.values = []
        self.nodes = []

    def add_node(self, node):
        if node in self.nodes:
            return False
        self.nodes.append(node)
        for i in list(node.inputs.values()) + list(node.outputs.values()):
            if i not in self.values:
                self.values.append(i)
        return True

    def _merge_values(self, orig, copy):
        for i in self.nodes:
            for j in i.inputs.keys():
                if i.inputs[j] == copy:
                    i.inputs[j] = orig
            for j in i.outputs.keys():
                if i.outputs[j] == copy:
                    i.outputs[j] = orig
        self.values.remove(copy)

    def _merge_nodes(self, orig, copy):
        #if possibly, replace the less finished one
        if not orig.done:
            if copy.done or (copy.running and not orig.running):
                orig, copy = copy, orig
        for key, value in copy.outputs.items():
            if key in orig.outputs:
                self._merge_values(orig.outputs[key], value)
            else:
                value.depends = orig
                orig.outputs[key] = value
                if orig.done:
                    value.value = orig.results[key]
        self.nodes.remove(copy)

    def ready(self):
        return any(i.ready() for i in self.nodes)

    def done(self):
        return all(i.done() or i.error() for i in self.nodes)

    def error(self):
        return any(i.error() for i in self.nodes)

    def running(self):
        return any(i.running() for i in self.nodes)

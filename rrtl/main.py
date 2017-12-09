import sys
import argparse
import rrtl

def main():
  argp = argparse.ArgumentParser()
  argp.add_argument('--input', '-i', default='input.txt')
  argp.add_argument('--debug', dest='debug', action='store_true')
  argp.add_argument('--no-debug', dest='debug', action='store_false')
  argp.set_defaults(debug=False)

  args = argp.parse_args()

  rrtl.Debug.debug_on = args.debug
  graph = rrtl.Graph()
  clauses_set = rrtl.ClausesSet()
  parser = rrtl.Parser(graph, clauses_set)

  with open(args.input, 'r') as input:
    spec = input.read()
    print(spec)
    parser.parseSpec2Graph(spec)

  cycles = graph.shrink()
  print('Total cycles found: %d' % (len(cycles)))
  for cycle in cycles: print(cycle)

  print(clauses_set)
  unsatisfiable = rrtl.Verifier(clauses_set, cycles).verify()
  print('unsatisfiable: ', unsatisfiable)


if __name__ == '__main__': main()

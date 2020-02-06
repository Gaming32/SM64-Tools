import importlib, sys, shlex

modules = {
    'script': 'sm64tools.bscript',
}

def main():
    if sys.argv[1] == '-h' or sys.argv[1] == '--help':
        print('Usage: "%s" -m sm64tools [-h] <module>' % sys.executable)
        print('You can use the following modules:')
        for mod in modules:
            print('+', mod)
        return
    if sys.argv[1] in modules:
        importlib.import_module(modules[sys.argv[1]]).main(sys.argv[2:])
    else:
        print('not a valid module, "%s"' % sys.argv[1])

if __name__ == '__main__': main()
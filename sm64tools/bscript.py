import sys, argparse
import string

#region Old Header
# commands = {
#     'start': {
#         'code': 0x00,
#         'args': [],
#     },
#     'end': {
#         'code': 0x0A,
#         'args': [],
#     },
#     'loopstart': {
#         'code': 0x05,
#         'args': [
#             {
#                 'required': True,
#                 'type': int,
#             }
#         ],
#     },
#     'loopend': {
#         'code': 0x06,
#         'args': [],
#     },
# }
#endregion

blocks = [
    'script',
    'loop',
    'gameloop',
]

def _sections(data, count):
    for i in range(0, len(data), count):
        try: d = data[i:i+count]
        except IndentationError: d = data[i:]
        yield d

def bytes_type(value):
    value = value.lower()
    for white in string.whitespace:
        value = value.replace(white, '')
    res = b''
    for byte in _sections(value, 2):
        if len(byte) < 2:
            byte += '0'
        res += eval("b'\\x%s'" % byte)
    return res
def inv_bytes_type(data, mode=1):
    if mode == 0:
        return ''.join(hex(byte)[2:].zfill(2) for byte in data)
    elif mode == 1:
        return ' '.join(hex(byte)[2:].upper().zfill(2) for byte in data)

def _comp_arg_parse(args):
    arglist = []
    statedict = {
        'data': '',
        'in_string': False,
        'in_escape': False
    }
    for char in args:
        if char == '#':
            if not statedict['in_string']:
                break
        elif char == ',':
            if not statedict['in_string']:
                arglist.append(statedict['data'])
            else:
                statedict['data'] += ','
        elif char in string.whitespace:
            if statedict['in_string']:
                statedict['data'] += char
        elif char == '"':
            if not statedict['in_escape']:
                statedict['in_string'] = not statedict['in_string']
            else:
                statedict['in_escape'] = False
                statedict['data'] += '"'
        elif char == '\\':
            statedict['in_escape'] = not statedict['in_escape']
            if not statedict['in_escape']:
                statedict['data'] += '\\'
        else:
            statedict['data'] += char
    if statedict['data']:
        arglist.append(statedict['data'])
    return arglist

def _command(command, args, funcs):
    res = b''
    if command == 'bytecode':
        res += bytes_type(''.join(args))

    elif command == 'script':
        res += b'\x00'
        if len(args) > 0:
            res += int(args[0], base=0).to_bytes(1, 'big')
        else:
            res += b'\x00'
        res += b'\0\0'
    elif command == 'scriptend':
        res += b'\x0A'
        res += b'\0\0\0'
    elif command == 'gameloop':
        res += b'\x08'
        res += b'\0\0\0'
    elif command == 'gameloopend':
        res += b'\x09'
        res += b'\0\0\0'
    elif command == 'loop':
        res += b'\x05'
        res += b'\0'
        res += int(args[0], base=0).to_bytes(2, 'big')
    elif command == 'loopend':
        res += b'\x06'
        res += b'\0\0\0'
    
    elif command == 'modelid':
        res += b'\x1B'
        res += b'\0'
    elif command == 'deactivate':
        res += b'\x1D'
        res += b'\0\0\0'
    elif command == 'droptoground':
        res += b'\x1E'
        res += b'\0\0\0'
    elif command == 'animate':
        res += b'\x28'
        res += (int(args[0], base=0) // 4).to_bytes(1, 'big')
        res += b'\0\0'
    elif command == 'storinitpos':
        res += b'\x2D'
        res += b'\0\0\0'
    elif command == 'scale':
        res += b'\x32'
        res += b'\0'
        res += int(args[0], base=0).to_bytes(2, 'big')

    return res

def _comp_command(command, context):
    pass

def script_compile(file, return_context=False):
    context = {
        'funcs': [],
        'preset': None,
    }
    res = b''
    layer = []
    for line in file:
        line = line.strip()
        if ' ' in line:
            command, args = line.split(' ', 1)
            if '#' in command:
                command = command.split('#')[0]
                args = ''
            args = _comp_arg_parse(args)
        else:
            command = line
            args = []
        if command in blocks and args and args[-1].endswith('{'):
            args[-1] = args[-1][:-1]
            if not args[-1]:
                args.pop()
            layer.append(command)
        elif command == '}':
            command = layer.pop() + 'end'
        res += _command(command, args, context['funcs'])
    if return_context:
        res = (res, context)
    return res

def main(args=sys.argv[1:]):
    # parser = argparse.ArgumentParser(prog='python -m sm64tools script')
    parser = argparse.ArgumentParser(description='tools for behavior scripting')
    subp_man = parser.add_subparsers(title='job', dest='job', help="the job to do stuff. run 'sm64tools script <job> --help' for more info")

    comp_parser = subp_man.add_parser('compile', description='compiles the specified script and prints the output')
    comp_parser.add_argument('file', type=argparse.FileType('r'), help='the script to compile')
    comp_parser.add_argument('-t', '--output-type', dest='output_type', choices=['flat', 'pretty'], default='pretty',
        help="the way to display the compiled bytecode. 'flat' looks like this: 1a3d9f; 'pretty' looks like this: 1A 3D 9F. defaults to 'pretty'")

    args = parser.parse_args(args)
    if args.job == 'compile':
        comp = script_compile(args.file)
        if args.output_type == 'flat':
            output_type = 0
        elif args.output_type == 'pretty':
            output_type = 1
        print(inv_bytes_type(comp, output_type))

if __name__ == '__main__': main()
    # script_compile(open('example_loop.mbs'))
    # script_compile(open('example_load.mbs'))
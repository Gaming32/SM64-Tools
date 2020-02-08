import json
fin = open('presetdict.txt', encoding='utf-8')
res = {}
header = False
for line in fin:
    if line.startswith('ROM Addr: '):
        line = line.split()
        addr = int(line[2], 16)
        if 'name' in globals():
            res[name]['length'] = addr - res[name]['addr']
        header = True
        continue
    if header:
        name = line.strip()
        if name.endswith(' Behavior'):
            name = name[:-len(' Behavior')]
        name = name.lower()
        res[name] = {}
        res[name]['addr'] = addr
        header = False
        continue
res[name]['length'] = 0x1C
# __import__('pprint').pprint(res)
fout = open(r'.\sm64tools\presetdict.json', 'w', encoding='utf-8')
json.dump(res, fout, indent=4)
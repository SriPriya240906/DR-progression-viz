import sys
p='requirements.txt'
# Read raw
b=open(p,'rb').read()
# try utf-16 then utf-8
for enc in ('utf-16','utf-8'):
    try:
        s=b.decode(enc)
        break
    except Exception:
        s=None
if s is None:
    print('UNKNOWN_ENCODING')
    sys.exit(1)
if 'reportlab==5.0.0' in s:
    print('ALREADY_PRESENT')
    sys.exit(0)
# append and write back with same encoding
s=s.rstrip()+"\nreportlab==5.0.0\n"
with open(p,'w',encoding=enc) as f:
    f.write(s)
print('ADDED',enc)

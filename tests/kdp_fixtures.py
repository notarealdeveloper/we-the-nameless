"""Tiny hand-written PDFs: no TeX or book sources involved."""
from pathlib import Path


def pdf(path, contents=None, extra='', resources='<< >>', box='0 0 504 720'):
    contents = contents or [b'0.2 0.4 0.7 rg 60 60 180 100 re f\n']
    objects = ['<< /Type /Catalog /Pages 2 0 R >>'.encode(),
        ('<< /Type /Pages /Count %d /Kids [%s] >>' % (len(contents), ' '.join(f'{3+2*i} 0 R' for i in range(len(contents))))).encode()]
    for i, content in enumerate(contents):
        objects += [(f'<< /Type /Page /Parent 2 0 R /MediaBox [{box}] /Resources {resources} /Contents {4+2*i} 0 R {extra} >>').encode(),
                    f'<< /Length {len(content)} >>\nstream\n'.encode() + content + b'endstream']
    data = b'%PDF-1.7\n'; offsets = [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(data)); data += f'{number} 0 obj\n'.encode() + obj + b'\nendobj\n'
    xref = len(data)
    data += f'xref\n0 {len(offsets)}\n0000000000 65535 f \n'.encode()
    data += b''.join(f'{offset:010d} 00000 n \n'.encode() for offset in offsets[1:])
    data += f'trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode()
    Path(path).write_bytes(data)

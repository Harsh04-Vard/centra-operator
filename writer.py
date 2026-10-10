import base64, sys, json, pathlib

def write_files(data):
    for path, material in data.items():
        p = pathlib.Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        content = base64.b64decode(material)
        p.write_bytes(content)
        print(f"[OK] Written {path} ({len(content)} bytes)")

if __name__ == '__main__':
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        write_files(json.load(f))

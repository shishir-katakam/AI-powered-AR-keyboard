import re

path = (
    r'C:\Users\natra\AppData\Local\Packages'
    r'\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0'
    r'\LocalCache\local-packages\Python313\site-packages'
    r'\mediapipe\tasks\python\vision\drawing_utils.py'
)

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Nuke everything between 'import cv2' and 'import numpy' and replace cleanly
content = re.sub(
    r'(import cv2\n).*?(import numpy as np)',
    r'\1try:\n    import matplotlib.pyplot as plt\nexcept ImportError:\n    plt = None\nimport numpy as np',
    content,
    flags=re.DOTALL
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Patched successfully')
print('Verify:')
for i, line in enumerate(content.splitlines()[18:28], 19):
    print(f'{i}: {line}')

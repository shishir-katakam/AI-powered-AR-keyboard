"""
Runtime hook: stub out matplotlib so mediapipe's drawing_utils
doesn't crash on import. The app doesn't use drawing_utils at all.
Uses a plain stub class instead of unittest.mock to avoid import issues.
"""
import sys
import types

class _Stub:
    """A dummy object that returns itself for any attribute / call."""
    def __getattr__(self, name):
        return _Stub()
    def __call__(self, *args, **kwargs):
        return _Stub()
    def __iter__(self):
        return iter([])
    def __bool__(self):
        return False

# Pre-register matplotlib and every sub-module mediapipe might touch
for mod_name in [
    'matplotlib', 'matplotlib.pyplot', 'matplotlib.patches',
    'matplotlib.collections', 'matplotlib.lines',
    'matplotlib.figure', 'matplotlib.axes',
    'matplotlib.colors', 'matplotlib.cm',
]:
    mod = types.ModuleType(mod_name)
    mod.__dict__.setdefault('__path__', [])
    mod.__dict__.setdefault('__file__', mod_name)
    # Make any attribute access return the stub
    mod.__class__ = type(mod_name, (types.ModuleType,), {
        '__getattr__': lambda self, name: _Stub(),
    })
    sys.modules[mod_name] = mod

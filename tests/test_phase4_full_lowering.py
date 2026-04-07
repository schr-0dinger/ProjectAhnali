from dsl.analyzer import analyze_features, select_runtime_modules
from dsl.app import activity, app, ui, text, button, on_click


def test_decorator_runtime_emits_helper():
    source = """
def my_decorator(func):
    return func

@my_decorator
def handler():
    pass

app(activity("Test", ui(button("Click", id="btn")), on_click("btn", [])))
"""
    profile = analyze_features(source)
    modules = select_runtime_modules(profile)
    module_names = {m.name for m in modules}

    assert "python.advanced.decorators" in module_names
    assert any(m.helper_class_desc == "Lcom/ahnali/runtime/DecoratorRuntime;" for m in modules)


def test_context_manager_runtime_emits_helper():
    source = """
with open("test.txt") as f:
    x = 1

app(activity("Test", ui(text("Test", id="lbl")), []))
"""
    profile = analyze_features(source)
    modules = select_runtime_modules(profile)
    module_names = {m.name for m in modules}

    assert "python.advanced.context_managers" in module_names


def test_varargs_runtime_emits_helper():
    source = """
def func(*args, **kwargs):
    pass

app(activity("Test", ui(text("Test", id="lbl")), []))
"""
    profile = analyze_features(source)
    modules = select_runtime_modules(profile)
    module_names = {m.name for m in modules}

    assert "python.advanced.varargs" in module_names
    assert any(m.helper_class_desc == "Lcom/ahnali/runtime/VarargsRuntime;" for m in modules)


def test_inheritance_runtime_emits_helper():
    source = """
class Dog(Animal):
    pass

app(activity("Test", ui(text("Test", id="lbl")), []))
"""
    profile = analyze_features(source)
    modules = select_runtime_modules(profile)
    module_names = {m.name for m in modules}

    assert "python.oop.inheritance" in module_names
    assert any(m.helper_class_desc == "Lcom/ahnali/runtime/InheritanceRuntime;" for m in modules)


def test_descriptor_runtime_emits_helper():
    source = """
class Descriptor:
    def __get__(self, obj, objtype=None):
        pass

app(activity("Test", ui(text("Test", id="lbl")), []))
"""
    profile = analyze_features(source)
    modules = select_runtime_modules(profile)
    module_names = {m.name for m in modules}

    assert "python.oop.descriptors" in module_names
    assert any(m.helper_class_desc == "Lcom/ahnali/runtime/DescriptorRuntime;" for m in modules)


def test_metaclass_runtime_emits_helper():
    source = """
class MyMeta(type):
    pass

class MyClass(metaclass=MyMeta):
    pass

app(activity("Test", ui(text("Test", id="lbl")), []))
"""
    profile = analyze_features(source)
    modules = select_runtime_modules(profile)
    module_names = {m.name for m in modules}

    assert "python.oop.metaclasses" in module_names
    assert any(m.helper_class_desc == "Lcom/ahnali/runtime/MetaclassRuntime;" for m in modules)
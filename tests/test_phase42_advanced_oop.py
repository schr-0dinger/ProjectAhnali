from dsl.analyzer import analyze_features, select_runtime_modules


def test_class_inheritance_is_detected():
    source = """
class Dog(Animal):
    pass
"""
    profile = analyze_features(source)

    assert profile.classes["class"] is True
    assert profile.classes["inheritance"] is True


def test_descriptors_are_detected():
    source = """
class Descriptor:
    def __get__(self, obj, objtype=None):
        return self.value
    def __set__(self, obj, value):
        self.value = value
"""
    profile = analyze_features(source)

    assert profile.classes["descriptors"] is True


def test_metaclass_is_detected():
    source = """
class MyMeta(type):
    pass

class MyClass(metaclass=MyMeta):
    pass
"""
    profile = analyze_features(source)

    assert profile.classes["metaclasses"] is True


def test_getattribute_is_detected():
    source = """
class MyClass:
    def __getattribute__(self, name):
        return super().__getattribute__(name)
"""
    profile = analyze_features(source)

    assert profile.classes["getattribute"] is True


def test_inheritance_runtime_module_selected():
    source = """
class Dog(Animal):
    pass
"""
    profile = analyze_features(source)
    modules = select_runtime_modules(profile)
    names = {module.name for module in modules}

    assert "python.oop.inheritance" in names


def test_descriptors_runtime_module_selected():
    source = """
class Descriptor:
    def __get__(self, obj, objtype=None):
        pass
"""
    profile = analyze_features(source)
    modules = select_runtime_modules(profile)
    names = {module.name for module in modules}

    assert "python.oop.descriptors" in names


def test_metaclass_runtime_module_selected():
    source = """
class MyMeta(type):
    pass

class MyClass(metaclass=MyMeta):
    pass
"""
    profile = analyze_features(source)
    modules = select_runtime_modules(profile)
    names = {module.name for module in modules}

    assert "python.oop.metaclasses" in names
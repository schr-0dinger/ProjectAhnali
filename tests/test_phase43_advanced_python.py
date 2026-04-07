from dsl.analyzer import analyze_features, select_runtime_modules


def test_decorators_are_detected():
    source = """
def my_decorator(func):
    return func

@my_decorator
def decorated():
    pass
"""
    profile = analyze_features(source)

    assert profile.functions["decorators"] is True


def test_varargs_are_detected():
    source = """
def func(*args, **kwargs):
    pass
"""
    profile = analyze_features(source)

    assert profile.functions["varargs"] is True


def test_with_statement_is_detected():
    source = """
def read_file():
    with open("test.txt") as f:
        return f.read()
"""
    profile = analyze_features(source)

    assert profile.control_flow["with"] is True


def test_decorator_runtime_module_selected():
    source = """
def my_decorator(func):
    return func

@my_decorator
def handler():
    pass
"""
    profile = analyze_features(source)
    modules = select_runtime_modules(profile)
    names = {module.name for module in modules}

    assert "python.advanced.decorators" in names


def test_context_manager_runtime_module_selected():
    source = """
def read_file():
    with open("test.txt") as f:
        pass
"""
    profile = analyze_features(source)
    modules = select_runtime_modules(profile)
    names = {module.name for module in modules}

    assert "python.advanced.context_managers" in names


def test_varargs_runtime_module_selected():
    source = """
def func(*args):
    pass
"""
    profile = analyze_features(source)
    modules = select_runtime_modules(profile)
    names = {module.name for module in modules}

    assert "python.advanced.varargs" in names
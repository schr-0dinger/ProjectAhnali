from dsl.analyzer import analyze_features, select_runtime_modules


def test_async_features_are_detected():
    source = """
async def fetch_data():
    result = await get_data()
    yield result
    return result
"""
    profile = analyze_features(source)

    assert profile.async_features["async_def"] is True
    assert profile.async_features["await"] is True
    assert profile.async_features["yield"] is True


def test_yield_from_is_detected():
    source = """
def gen():
    yield from [1, 2, 3]
"""
    profile = analyze_features(source)

    assert profile.async_features["yield_from"] is True


def test_async_runtime_module_selected_when_async_def_detected():
    source = """
async def handler():
    pass
"""
    profile = analyze_features(source)
    modules = select_runtime_modules(profile)
    names = {module.name for module in modules}

    assert "python.async.async_runtime" in names


def test_generator_runtime_module_selected_when_yield_detected():
    source = """
def numbers():
    yield 1
    yield 2
"""
    profile = analyze_features(source)
    modules = select_runtime_modules(profile)
    names = {module.name for module in modules}

    assert "python.generators.iterator_runtime" in names
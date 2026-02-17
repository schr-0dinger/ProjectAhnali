from dsl import api as legacy_api
from dsl.api_domains import capabilities, hybrid, interaction, motion, state, structure, style


def test_api_domain_modules_expose_legacy_compatible_symbols():
    assert structure.app is legacy_api.app
    assert structure.activity is legacy_api.activity
    assert structure.Frame is legacy_api.Frame
    assert structure.frame is legacy_api.frame
    assert style.theme is legacy_api.theme
    assert interaction.on_click is legacy_api.on_click
    assert state.storage_put is legacy_api.storage_put
    assert capabilities.open_url is legacy_api.open_url
    assert motion.animate is legacy_api.animate


def test_hybrid_domain_placeholder_is_stable():
    assert hybrid.HYBRID_API_STATUS == "planned"

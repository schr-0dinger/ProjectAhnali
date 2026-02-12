from apk.toolchain import _select_manifest_theme


def test_select_manifest_theme_uses_material_components_when_material_present_no_action_bar():
    theme = _select_manifest_theme(
        extra_aars=["/tmp/material-1.12.0.aar", "/tmp/appcompat-1.6.1.aar"],
        show_action_bar=False,
    )
    assert theme == "@style/Theme.MaterialComponents.Light.NoActionBar"


def test_select_manifest_theme_uses_material_components_when_material_present_with_action_bar():
    theme = _select_manifest_theme(
        extra_aars=["/tmp/material-1.12.0.aar"],
        show_action_bar=True,
    )
    assert theme == "@style/Theme.MaterialComponents.Light"


def test_select_manifest_theme_keeps_platform_theme_without_material():
    theme = _select_manifest_theme(
        extra_aars=["/tmp/constraintlayout-2.1.4.aar"],
        show_action_bar=False,
    )
    assert theme == "@android:style/Theme.Material.Light.NoActionBar"

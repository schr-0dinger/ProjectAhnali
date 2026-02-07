# tests/test_omega_toolchain_scaffold.py


from apk.toolchain import emit_build_dir_from_program
from apk.project import render_manifest
from dsl.app import app, activity, assign, button, const, method, on_click, program, ret, state, text, ui


def test_emit_build_dir_writes_smali(tmp_path):
    out_dir = emit_build_dir_from_program(
        [assign("x", const(1))],
        out_dir=tmp_path,
        class_name="LTest;",
    )

    smali_path = out_dir / "smali" / "Test.smali"
    assert smali_path.exists()
    smali_text = smali_path.read_text(encoding="utf-8")
    assert ".class public LTest;" in smali_text


def test_emit_build_dir_with_wrapper_writes_activity_and_main(tmp_path):
    out_dir = emit_build_dir_from_program(
        [assign("x", const(1))],
        out_dir=tmp_path,
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc="Lcom/anali/preview/MainActivity;",
    )

    main_path = out_dir / "smali" / "Test.smali"
    activity_path = out_dir / "smali" / "com" / "anali" / "preview" / "MainActivity.smali"

    assert main_path.exists()
    assert activity_path.exists()

    main_text = main_path.read_text(encoding="utf-8")
    activity_text = activity_path.read_text(encoding="utf-8")

    assert ".class public LTest;" in main_text
    assert ".class public Lcom/anali/preview/MainActivity;" in activity_text
    assert "invoke-static {}, LTest;->main()V" in activity_text


def test_emit_build_dir_writes_resources_from_program(tmp_path):
    prog = program(
        [
            method(
                "main",
                return_type=None,
                body=[assign("x", const(1)), ret()],
            )
        ],
        resources={"app_name": "Widget Zoo", "greeting": "Hello"},
    )

    out_dir = emit_build_dir_from_program(
        prog,
        out_dir=tmp_path,
        class_name="LTest;",
    )

    strings_path = out_dir / "res" / "values" / "strings.xml"
    assert strings_path.exists()
    xml = strings_path.read_text(encoding="utf-8")
    assert '<string name="app_name">Widget Zoo</string>' in xml
    assert '<string name="greeting">Hello</string>' in xml


def test_emit_build_dir_writes_typed_resources_from_program(tmp_path):
    prog = program(
        [
            method(
                "main",
                return_type=None,
                body=[assign("x", const(1)), ret()],
            )
        ],
        resources={"app_name": "Widget Zoo"},
        resource_colors={"primary": "#FF112233"},
        resource_dimens={"pad_md": "16dp"},
        resource_styles={"AppTheme": {"android:colorPrimary": "@color/primary"}},
    )

    out_dir = emit_build_dir_from_program(
        prog,
        out_dir=tmp_path,
        class_name="LTest;",
    )

    colors_path = out_dir / "res" / "values" / "colors.xml"
    dimens_path = out_dir / "res" / "values" / "dimens.xml"
    styles_path = out_dir / "res" / "values" / "styles.xml"

    assert colors_path.exists()
    assert dimens_path.exists()
    assert styles_path.exists()

    colors_xml = colors_path.read_text(encoding="utf-8")
    dimens_xml = dimens_path.read_text(encoding="utf-8")
    styles_xml = styles_path.read_text(encoding="utf-8")
    assert '<color name="primary">#FF112233</color>' in colors_xml
    assert '<dimen name="pad_md">16dp</dimen>' in dimens_xml
    assert '<style name="apptheme">' in styles_xml


def test_manifest_defaults_to_app_name_resource_label():
    manifest = render_manifest()
    assert 'android:label="@string/app_name"' in manifest


@on_click("inc")
def _inc():
    count += 1
    label.text = f"Count: {count}"


def test_emit_build_dir_writes_split_handler_class_and_listener_target(tmp_path):
    prog = app(
        activity(
            "MainActivity",
            state(count=0),
            ui(
                text("Count: 0", id="label"),
                button("+", id="inc"),
            ),
            _inc,
        )
    ).build()

    out_dir = emit_build_dir_from_program(
        prog,
        out_dir=tmp_path / "build",
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_target_sig="(Landroid/app/Activity;)V",
    )

    handlers_path = out_dir / "smali" / "TestHandlers.smali"
    listener_path = out_dir / "smali" / "com" / "anali" / "preview" / "AnaliClickListener_inc.smali"
    assert handlers_path.exists()
    assert listener_path.exists()
    listener_text = listener_path.read_text(encoding="utf-8")
    assert "invoke-static {p1}, LTestHandlers;->onClick_inc(Landroid/view/View;)V" in listener_text

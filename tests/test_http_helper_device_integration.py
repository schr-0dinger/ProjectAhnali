import contextlib
import os
import shutil
import subprocess
import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from apk.toolchain import (
    _collect_toolchain_diagnostics,
    emit_build_dir_from_program,
    package_apk_from_dex,
    run_smali,
)
from dsl.app import (
    assign,
    call,
    const,
    method,
    new,
    program,
    ret,
    var,
)
from dsl.capabilities import resolve_runtime_bindings


HTTP_HELPER_DESC = "Lcom/ahnali/runtime/HttpHelper;"
CANCEL_RUNNABLE_DESC = "Lcom/ahnali/preview/AhnaliCancelProbeRunnable;"
TRANSPORT_RUNNABLE_DESC = "Lcom/ahnali/preview/AhnaliTransportProbeRunnable;"
WRAPPER_DESC = "Lcom/ahnali/preview/MainActivity;"


def _adb_path() -> str | None:
    path = shutil.which("adb")
    if path:
        return path
    sdk = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
    if sdk:
        candidate = Path(sdk) / "platform-tools" / "adb"
        if candidate.exists():
            return str(candidate)
    return None


def _has_device(adb: str) -> bool:
    try:
        result = subprocess.run([adb, "devices"], check=True, capture_output=True, text=True)
    except Exception:
        return False
    lines = [line.strip() for line in result.stdout.splitlines()[1:] if line.strip()]
    return any(line.split()[1] == "device" for line in lines if len(line.split()) >= 2)


def _skip_if_missing_device():
    issues = _collect_toolchain_diagnostics(require_adb=True)
    if issues:
        pytest.skip("; ".join(issues))
    adb = _adb_path()
    if not adb:
        pytest.skip("adb not found")
    if not _has_device(adb):
        pytest.skip("no adb devices in 'device' state")
    return adb


@dataclass
class _CapturedRequest:
    path: str
    method: str
    headers: dict[str, str]
    body: str


class _CaptureStore:
    def __init__(self):
        self._lock = threading.Lock()
        self.transport: list[_CapturedRequest] = []
        self.race: list[_CapturedRequest] = []

    def add(self, req: _CapturedRequest):
        with self._lock:
            if req.path.startswith("/transport"):
                self.transport.append(req)
            elif req.path.startswith("/race"):
                self.race.append(req)

    def snapshot(self):
        with self._lock:
            return list(self.transport), list(self.race)


def _handler_factory(store: _CaptureStore):
    class _Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):  # pragma: no cover - noisy httpd logs
            return

        def do_GET(self):
            self._handle()

        def do_POST(self):
            self._handle()

        def _handle(self):
            raw_len = self.headers.get("Content-Length", "0").strip() or "0"
            try:
                n = int(raw_len)
            except Exception:
                n = 0
            payload = self.rfile.read(n) if n > 0 else b""
            req = _CapturedRequest(
                path=self.path,
                method=self.command,
                headers={k.lower(): v for k, v in self.headers.items()},
                body=payload.decode("utf-8", errors="replace"),
            )
            store.add(req)

            if self.path.startswith("/transport"):
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"transport-ok")
                return
            if self.path.startswith("/race"):
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"race-ok")
                return
            self.send_response(404)
            self.end_headers()

    return _Handler


@contextlib.contextmanager
def _capture_server():
    store = _CaptureStore()
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _handler_factory(store))
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield store, int(httpd.server_address[1])
    finally:
        httpd.shutdown()
        thread.join(timeout=2.0)
        httpd.server_close()


def _smali_jar():
    return os.environ.get("SMALI_JAR")


def _transport_program(*, transport_url: str):
    body = [
        assign(
            "probe",
            new(
                TRANSPORT_RUNNABLE_DESC,
                args=[var("ctx"), const(transport_url)],
                arg_types=["Landroid/app/Activity;", "Ljava/lang/String;"],
            ),
        ),
        assign(
            "probe_token",
            call(
                "startAsync",
                args=[var("probe")],
                return_type="I",
                arg_types=["Ljava/lang/Runnable;"],
                invoke_kind="static",
                owner=HTTP_HELPER_DESC,
            ),
        ),
        assign(
            "transport_main_log",
            call(
                "i",
                args=[const("AHNALI_TRANSPORT_MAIN"), const("STARTED")],
                return_type="I",
                arg_types=["Ljava/lang/String;", "Ljava/lang/String;"],
                invoke_kind="static",
                owner="Landroid/util/Log;",
            ),
        ),
        ret(),
    ]
    p = program(
        [
            method(
                "main",
                params=["ctx"],
                param_types=["Landroid/app/Activity;"],
                return_type=None,
                body=body,
            )
        ]
    )
    p.capability_runtime_bindings = resolve_runtime_bindings(["Networking"])
    return p


def _race_program(*, race_count: int):
    body = []
    for i in range(race_count):
        t = f"t{i}"
        r = f"r{i}"
        body.append(
            assign(
                t,
                call(
                    "nextAsyncToken",
                    args=[],
                    return_type="I",
                    arg_types=[],
                    invoke_kind="static",
                    owner=HTTP_HELPER_DESC,
                ),
            )
        )
        body.append(
            assign(
                r,
                new(
                    CANCEL_RUNNABLE_DESC,
                    args=[var(t), const(120)],
                    arg_types=["I", "I"],
                ),
            )
        )
        body.append(
            assign(
                f"start{i}",
                call(
                    "startAsyncWithToken",
                    args=[var(t), var(r)],
                    return_type="I",
                    arg_types=["I", "Ljava/lang/Runnable;"],
                    invoke_kind="static",
                    owner=HTTP_HELPER_DESC,
                ),
            )
        )
        body.append(
            assign(
                f"cancel{i}",
                call(
                    "cancelAsync",
                    args=[var(t)],
                    return_type="I",
                    arg_types=["I"],
                    invoke_kind="static",
                    owner=HTTP_HELPER_DESC,
                ),
            )
        )

    body.append(
        assign(
            "race_main_log",
            call(
                "i",
                args=[const("AHNALI_RACE_MAIN"), const("STARTED")],
                return_type="I",
                arg_types=["Ljava/lang/String;", "Ljava/lang/String;"],
                invoke_kind="static",
                owner="Landroid/util/Log;",
            ),
        )
    )
    body.append(ret())

    p = program(
        [
            method(
                "main",
                params=["ctx"],
                param_types=["Landroid/app/Activity;"],
                return_type=None,
                body=body,
            )
        ]
    )
    p.capability_runtime_bindings = resolve_runtime_bindings(["Networking"])
    return p


def _emit_cancel_probe_runnable(smali_root: Path):
    smali_path = smali_root / "com" / "ahnali" / "preview" / "AhnaliCancelProbeRunnable.smali"
    smali_path.parent.mkdir(parents=True, exist_ok=True)
    smali_path.write_text(
        "\n".join(
            [
                ".class public Lcom/ahnali/preview/AhnaliCancelProbeRunnable;",
                ".super Ljava/lang/Object;",
                ".implements Ljava/lang/Runnable;",
                "",
                ".field private final mToken:I",
                ".field private final mDelayMs:I",
                "",
                ".method public constructor <init>(II)V",
                "    .locals 0",
                "    invoke-direct {p0}, Ljava/lang/Object;-><init>()V",
                "    iput p1, p0, Lcom/ahnali/preview/AhnaliCancelProbeRunnable;->mToken:I",
                "    iput p2, p0, Lcom/ahnali/preview/AhnaliCancelProbeRunnable;->mDelayMs:I",
                "    return-void",
                ".end method",
                "",
                ".method public run()V",
                "    .locals 5",
                "    iget v0, p0, Lcom/ahnali/preview/AhnaliCancelProbeRunnable;->mDelayMs:I",
                "    int-to-long v1, v0",
                "    :ahnali_cancel_probe_sleep_try_start",
                "    invoke-static {v1, v2}, Ljava/lang/Thread;->sleep(J)V",
                "    :ahnali_cancel_probe_sleep_try_end",
                "    .catch Ljava/lang/InterruptedException; {:ahnali_cancel_probe_sleep_try_start .. :ahnali_cancel_probe_sleep_try_end} :ahnali_cancel_probe_sleep_catch",
                "    iget v0, p0, Lcom/ahnali/preview/AhnaliCancelProbeRunnable;->mToken:I",
                "    invoke-static {v0}, Lcom/ahnali/runtime/HttpHelper;->shouldCancel(I)I",
                "    move-result v3",
                "    if-eqz v3, :ahnali_cancel_probe_not_cancelled",
                "    const/4 v4, 0x7",
                "    invoke-static {v0, v4}, Lcom/ahnali/runtime/HttpHelper;->setAsyncError(II)V",
                '    const-string v2, "AHNALI_RACE"',
                "    invoke-static {v4}, Ljava/lang/String;->valueOf(I)Ljava/lang/String;",
                "    move-result-object v1",
                "    invoke-static {v2, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I",
                "    move-result v2",
                "    return-void",
                "    :ahnali_cancel_probe_not_cancelled",
                "    const/4 v4, 0x0",
                "    invoke-static {v0, v4}, Lcom/ahnali/runtime/HttpHelper;->setAsyncError(II)V",
                '    const-string v2, "AHNALI_RACE"',
                "    invoke-static {v4}, Ljava/lang/String;->valueOf(I)Ljava/lang/String;",
                "    move-result-object v1",
                "    invoke-static {v2, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I",
                "    move-result v2",
                "    return-void",
                "    :ahnali_cancel_probe_sleep_catch",
                "    iget v0, p0, Lcom/ahnali/preview/AhnaliCancelProbeRunnable;->mToken:I",
                "    const/4 v4, 0x2",
                "    invoke-static {v0, v4}, Lcom/ahnali/runtime/HttpHelper;->setAsyncError(II)V",
                '    const-string v2, "AHNALI_RACE"',
                "    invoke-static {v4}, Ljava/lang/String;->valueOf(I)Ljava/lang/String;",
                "    move-result-object v1",
                "    invoke-static {v2, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I",
                "    move-result v2",
                "    return-void",
                ".end method",
            ]
        ),
        encoding="utf-8",
    )


def _emit_transport_probe_runnable(smali_root: Path):
    smali_path = smali_root / "com" / "ahnali" / "preview" / "AhnaliTransportProbeRunnable.smali"
    smali_path.parent.mkdir(parents=True, exist_ok=True)
    smali_path.write_text(
        "\n".join(
            [
                ".class public Lcom/ahnali/preview/AhnaliTransportProbeRunnable;",
                ".super Ljava/lang/Object;",
                ".implements Ljava/lang/Runnable;",
                "",
                ".field private final mCtx:Landroid/app/Activity;",
                ".field private final mUrl:Ljava/lang/String;",
                "",
                ".method public constructor <init>(Landroid/app/Activity;Ljava/lang/String;)V",
                "    .locals 0",
                "    invoke-direct {p0}, Ljava/lang/Object;-><init>()V",
                "    iput-object p1, p0, Lcom/ahnali/preview/AhnaliTransportProbeRunnable;->mCtx:Landroid/app/Activity;",
                "    iput-object p2, p0, Lcom/ahnali/preview/AhnaliTransportProbeRunnable;->mUrl:Ljava/lang/String;",
                "    return-void",
                ".end method",
                "",
                ".method public run()V",
                "    .locals 9",
                "    iget-object v0, p0, Lcom/ahnali/preview/AhnaliTransportProbeRunnable;->mCtx:Landroid/app/Activity;",
                "    iget-object v1, p0, Lcom/ahnali/preview/AhnaliTransportProbeRunnable;->mUrl:Ljava/lang/String;",
                '    const-string v2, "POST"',
                '    const-string v3, "X-Ahnali-Auth: token-1\\nContent-Type: text/plain"',
                '    const-string v4, "payload-1"',
                "    const/16 v5, 0xdac",
                "    invoke-static/range {v0 .. v5}, Lcom/ahnali/runtime/HttpHelper;->httpRequestStatusWithTimeout(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;I)I",
                "    move-result v6",
                '    const-string v5, "fallback"',
                "    const/16 v6, 0xdac",
                "    invoke-static/range {v0 .. v6}, Lcom/ahnali/runtime/HttpHelper;->httpRequestWithTimeout(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;I)Ljava/lang/String;",
                "    move-result-object v7",
                "    const/16 v5, 0xdac",
                "    invoke-static/range {v0 .. v5}, Lcom/ahnali/runtime/HttpHelper;->httpRequestErrorWithTimeout(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;I)I",
                "    move-result v8",
                '    const-string v0, "AHNALI_TRANSPORT"',
                '    const-string v1, "DONE"',
                "    invoke-static {v0, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I",
                "    move-result v2",
                "    return-void",
                ".end method",
            ]
        ),
        encoding="utf-8",
    )


def _build_and_run_app(
    *,
    frontend_ir,
    out_dir: Path,
    application_id: str,
    adb: str,
    emit_cancel_probe: bool = False,
    emit_transport_probe: bool = False,
):
    build_dir = emit_build_dir_from_program(
        frontend_ir,
        out_dir=out_dir,
        class_name="LTest;",
        emit_wrapper=True,
        wrapper_class_desc=WRAPPER_DESC,
        wrapper_target_desc="LTest;",
        wrapper_target_sig="(Landroid/app/Activity;)V",
    )
    if emit_cancel_probe:
        _emit_cancel_probe_runnable(build_dir / "smali")
    if emit_transport_probe:
        _emit_transport_probe_runnable(build_dir / "smali")
    subprocess.run([adb, "logcat", "-c"], check=False)
    dex_path = run_smali(
        build_dir / "smali",
        out_dir=build_dir / "classes.dex",
        smali_jar=_smali_jar(),
        api=21,
    )
    signed_apk = package_apk_from_dex(
        dex_path,
        out_dir=build_dir,
        application_id=application_id,
        activity_class_desc=WRAPPER_DESC,
        permissions=["android.permission.INTERNET"],
        target_sdk=27,
    )
    subprocess.run([adb, "uninstall", application_id], check=False, capture_output=True, text=True)
    subprocess.run([adb, "install", "-r", str(signed_apk)], check=True, capture_output=True, text=True)
    subprocess.run(
        [adb, "shell", "am", "start", "-W", "-n", f"{application_id}/com.ahnali.preview.MainActivity"],
        check=True,
    )


def _wait_until(predicate, *, timeout_s: float, step_s: float = 0.1) -> bool:
    end = time.time() + timeout_s
    while time.time() < end:
        if predicate():
            return True
        time.sleep(step_s)
    return False


def test_http_helper_device_transport_applies_headers_and_post_body(tmp_path):
    adb = _skip_if_missing_device()

    with _capture_server() as (store, port):
        subprocess.run([adb, "reverse", f"tcp:{port}", f"tcp:{port}"], check=True)
        try:
            frontend = _transport_program(transport_url=f"http://127.0.0.1:{port}/transport")
            _build_and_run_app(
                frontend_ir=frontend,
                out_dir=tmp_path / "transport_build",
                application_id="com.ahnali.itest.transport",
                adb=adb,
                emit_transport_probe=True,
            )

            ok = _wait_until(lambda: len(store.snapshot()[0]) >= 3, timeout_s=10.0)
            assert ok, "expected at least 3 transport requests from status/body/error calls"

            transport, _race = store.snapshot()
            assert len(transport) >= 3
            checked = transport[:3]
            for req in checked:
                assert req.method == "POST"
                assert req.headers.get("x-ahnali-auth") == "token-1"
                assert req.body == "payload-1"
        finally:
            subprocess.run([adb, "reverse", "--remove", f"tcp:{port}"], check=False)


def test_http_helper_device_concurrent_cancel_race_stress(tmp_path):
    adb = _skip_if_missing_device()
    race_count = 12

    frontend = _race_program(race_count=race_count)
    _build_and_run_app(
        frontend_ir=frontend,
        out_dir=tmp_path / "race_build",
        application_id="com.ahnali.itest.race",
        adb=adb,
        emit_cancel_probe=True,
    )

    def _race_codes():
        out = subprocess.run(
            [adb, "logcat", "-d", "-s", "AHNALI_RACE:I", "*:S"],
            check=False,
            capture_output=True,
            text=True,
        ).stdout
        vals = []
        for line in out.splitlines():
            if "AHNALI_RACE" not in line:
                continue
            msg = line.rsplit(":", 1)[-1].strip()
            try:
                vals.append(int(msg))
            except Exception:
                continue
        return vals

    ok = _wait_until(lambda: len(_race_codes()) >= race_count, timeout_s=15.0)
    assert ok, "expected one race log line per token"
    codes = _race_codes()[:race_count]
    assert len(codes) == race_count
    assert set(codes).issubset({0, 2, 7})
    assert any(code == 7 for code in codes)

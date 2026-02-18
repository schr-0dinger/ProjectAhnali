import json
from pathlib import Path

from tools.runtime_abi_snapshot import (
    build_runtime_abi_snapshot,
    check_runtime_abi_snapshot,
)


def _snapshot_classes(snapshot: dict) -> dict[str, set[str]]:
    return {
        str(entry["class_desc"]): set(entry["methods"])
        for entry in snapshot.get("classes", [])
    }


def test_runtime_abi_snapshot_matches_committed_contract():
    ok, message = check_runtime_abi_snapshot(Path("cfg/runtime_abi_snapshot_v1.json"))
    assert ok, message


def test_runtime_abi_snapshot_includes_http_helper_surface():
    snapshot = build_runtime_abi_snapshot()
    classes = _snapshot_classes(snapshot)
    http_methods = classes["Lcom/ahnali/runtime/HttpHelper;"]
    assert "httpRequestWithTimeout(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;I)Ljava/lang/String;" in http_methods
    assert "httpRequestStatusWithTimeout(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;I)I" in http_methods
    assert "httpRequestErrorWithTimeout(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;I)I" in http_methods
    assert "cancelAsync(I)I" in http_methods
    assert "getAsyncBody(ILjava/lang/String;)Ljava/lang/String;" in http_methods


def test_runtime_abi_snapshot_includes_permission_helper_surface():
    snapshot = build_runtime_abi_snapshot()
    classes = _snapshot_classes(snapshot)
    permission_methods = classes["Lcom/ahnali/runtime/PermissionHelper;"]
    assert "isGranted(Landroid/app/Activity;Ljava/lang/String;)I" in permission_methods


def test_runtime_abi_snapshot_includes_notification_helper_surface():
    snapshot = build_runtime_abi_snapshot()
    classes = _snapshot_classes(snapshot)
    notification_methods = classes["Lcom/ahnali/runtime/NotificationHelper;"]
    assert "createChannel(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I" in notification_methods
    assert (
        "postNotification(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I"
        in notification_methods
    )
    assert (
        "postNotificationError(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I"
        in notification_methods
    )


def test_runtime_abi_snapshot_includes_clipboard_helper_surface():
    snapshot = build_runtime_abi_snapshot()
    classes = _snapshot_classes(snapshot)
    clipboard_methods = classes["Lcom/ahnali/runtime/ClipboardHelper;"]
    assert "setText(Landroid/app/Activity;Ljava/lang/String;)I" in clipboard_methods
    assert "getText(Landroid/app/Activity;Ljava/lang/String;)Ljava/lang/String;" in clipboard_methods


def test_runtime_abi_snapshot_includes_sharing_helper_surface():
    snapshot = build_runtime_abi_snapshot()
    classes = _snapshot_classes(snapshot)
    sharing_methods = classes["Lcom/ahnali/runtime/ShareHelper;"]
    assert "shareText(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I" in sharing_methods
    assert "shareTextError(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I" in sharing_methods
    assert "shareFile(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I" in sharing_methods
    assert "shareFileError(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I" in sharing_methods
    assert "openUri(Landroid/app/Activity;Ljava/lang/String;)I" in sharing_methods
    assert "openUriError(Landroid/app/Activity;Ljava/lang/String;)I" in sharing_methods


def test_runtime_abi_snapshot_includes_deep_link_helper_surface():
    snapshot = build_runtime_abi_snapshot()
    classes = _snapshot_classes(snapshot)
    deep_link_methods = classes["Lcom/ahnali/runtime/DeepLinkHelper;"]
    assert "getLaunchUri(Landroid/app/Activity;Ljava/lang/String;)Ljava/lang/String;" in deep_link_methods
    assert "getLaunchUriError(Landroid/app/Activity;)I" in deep_link_methods


def test_runtime_abi_snapshot_includes_work_helper_surface():
    snapshot = build_runtime_abi_snapshot()
    classes = _snapshot_classes(snapshot)
    methods = classes["Lcom/ahnali/runtime/WorkHelper;"]
    assert "enqueueWork(Landroid/app/Activity;Ljava/lang/String;I)I" in methods
    assert "enqueueWorkError(Landroid/app/Activity;Ljava/lang/String;I)I" in methods
    assert "cancelWork(Landroid/app/Activity;Ljava/lang/String;)I" in methods
    assert "cancelWorkError(Landroid/app/Activity;Ljava/lang/String;)I" in methods
    assert "getWorkStatus(Landroid/app/Activity;Ljava/lang/String;)I" in methods
    assert "getWorkStatusError(Landroid/app/Activity;Ljava/lang/String;)I" in methods


def test_runtime_abi_snapshot_includes_alarm_helper_surface():
    snapshot = build_runtime_abi_snapshot()
    classes = _snapshot_classes(snapshot)
    methods = classes["Lcom/ahnali/runtime/AlarmHelper;"]
    assert "scheduleAlarm(Landroid/app/Activity;Ljava/lang/String;I)I" in methods
    assert "scheduleAlarmError(Landroid/app/Activity;Ljava/lang/String;I)I" in methods
    assert "cancelAlarm(Landroid/app/Activity;Ljava/lang/String;)I" in methods
    assert "cancelAlarmError(Landroid/app/Activity;Ljava/lang/String;)I" in methods
    assert "getAlarmStatus(Landroid/app/Activity;Ljava/lang/String;)I" in methods
    assert "getAlarmStatusError(Landroid/app/Activity;Ljava/lang/String;)I" in methods


def test_runtime_abi_snapshot_includes_job_helper_surface():
    snapshot = build_runtime_abi_snapshot()
    classes = _snapshot_classes(snapshot)
    methods = classes["Lcom/ahnali/runtime/JobHelper;"]
    assert "scheduleJob(Landroid/app/Activity;II)I" in methods
    assert "scheduleJobError(Landroid/app/Activity;II)I" in methods
    assert "cancelJob(Landroid/app/Activity;I)I" in methods
    assert "cancelJobError(Landroid/app/Activity;I)I" in methods
    assert "getJobStatus(Landroid/app/Activity;I)I" in methods
    assert "getJobStatusError(Landroid/app/Activity;I)I" in methods


def test_runtime_abi_snapshot_includes_web_helper_surface():
    snapshot = build_runtime_abi_snapshot()
    classes = _snapshot_classes(snapshot)
    web_methods = classes["Lcom/ahnali/runtime/WebHelper;"]
    assert "setPolicy(Landroid/app/Activity;IIII)I" in web_methods
    assert "addJsBridge(Landroid/app/Activity;Ljava/lang/String;)I" in web_methods
    assert "addJsBridgeError(Landroid/app/Activity;Ljava/lang/String;)I" in web_methods
    assert "chooseFile(Landroid/app/Activity;Ljava/lang/String;)I" in web_methods
    assert "chooseFileError(Landroid/app/Activity;Ljava/lang/String;)I" in web_methods
    assert "setCookie(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I" in web_methods
    assert "setCookieError(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I" in web_methods
    assert "getCookie(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;" in web_methods
    assert "getCookieError(Landroid/app/Activity;Ljava/lang/String;)I" in web_methods
    assert "loadUrl(Landroid/app/Activity;Ljava/lang/String;)I" in web_methods
    assert "loadUrlError(Landroid/app/Activity;Ljava/lang/String;)I" in web_methods


def test_runtime_abi_snapshot_includes_program5_storage_backend_surface():
    snapshot = build_runtime_abi_snapshot()
    classes = _snapshot_classes(snapshot)
    storage_methods = classes["Lcom/ahnali/runtime/StorageHelper;"]
    assert "dataStorePutString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I" in storage_methods
    assert "fileWriteString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I" in storage_methods
    assert "sqlitePutString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I" in storage_methods
    assert "roomPutString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I" in storage_methods
    assert "encryptedPutString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I" in storage_methods


def test_runtime_abi_snapshot_check_detects_drift(tmp_path):
    baseline = build_runtime_abi_snapshot()
    snapshot_path = tmp_path / "runtime_abi_snapshot_v1.json"
    snapshot_path.write_text(json.dumps(baseline, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    drifted = json.loads(snapshot_path.read_text(encoding="utf-8"))
    drifted["classes"][0]["methods"] = []
    snapshot_path.write_text(json.dumps(drifted, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    ok, message = check_runtime_abi_snapshot(snapshot_path)
    assert not ok
    assert "Runtime ABI snapshot drift detected." in message

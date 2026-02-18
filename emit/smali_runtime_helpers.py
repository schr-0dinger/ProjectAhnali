from __future__ import annotations

import re


_METHOD_SIG_RE = re.compile(r"^\((?P<args>.*)\)(?P<ret>.+)$")


def _split_arg_descs(arg_blob: str) -> list[str]:
    out: list[str] = []
    i = 0
    n = len(arg_blob)
    while i < n:
        c = arg_blob[i]
        if c in "ZBSCIFJDV":
            out.append(c)
            i += 1
            continue
        if c == "[":
            j = i
            while j < n and arg_blob[j] == "[":
                j += 1
            if j >= n:
                raise RuntimeError(f"Invalid method signature args: '{arg_blob}'")
            if arg_blob[j] == "L":
                k = arg_blob.find(";", j)
                if k == -1:
                    raise RuntimeError(f"Invalid method signature args: '{arg_blob}'")
                out.append(arg_blob[i : k + 1])
                i = k + 1
            else:
                out.append(arg_blob[i : j + 1])
                i = j + 1
            continue
        if c == "L":
            k = arg_blob.find(";", i)
            if k == -1:
                raise RuntimeError(f"Invalid method signature args: '{arg_blob}'")
            out.append(arg_blob[i : k + 1])
            i = k + 1
            continue
        raise RuntimeError(f"Unsupported descriptor token '{c}' in '{arg_blob}'")
    return out


def _parse_method_sig(sig: str) -> tuple[list[str], str]:
    m = _METHOD_SIG_RE.match(str(sig).strip())
    if not m:
        raise RuntimeError(f"Invalid method signature '{sig}'")
    args = _split_arg_descs(m.group("args"))
    ret = m.group("ret")
    return args, ret


def _emit_default_method_body(ret_desc: str) -> list[str]:
    if ret_desc == "V":
        return ["    return-void"]
    if ret_desc in {"J", "D"}:
        return [
            "    const-wide/16 v0, 0x0",
            "    return-wide v0",
        ]
    if ret_desc.startswith("L") or ret_desc.startswith("["):
        return [
            "    const/4 v0, 0x0",
            "    return-object v0",
        ]
    return [
        "    const/4 v0, 0x0",
        "    return v0",
    ]


def _emit_url_launcher_open_url_method() -> list[str]:
    return [
        ".method public static openUrl(Landroid/app/Activity;Ljava/lang/String;)I",
        "    .locals 3",
        "    if-eqz p0, :ahnali_url_fail",
        "    if-eqz p1, :ahnali_url_fail",
        "    :ahnali_url_try_start",
        '    const-string v0, "android.intent.action.VIEW"',
        "    new-instance v1, Landroid/content/Intent;",
        "    invoke-direct {v1, v0}, Landroid/content/Intent;-><init>(Ljava/lang/String;)V",
        "    invoke-static {p1}, Landroid/net/Uri;->parse(Ljava/lang/String;)Landroid/net/Uri;",
        "    move-result-object v2",
        "    invoke-virtual {v1, v2}, Landroid/content/Intent;->setData(Landroid/net/Uri;)Landroid/content/Intent;",
        "    invoke-virtual {p0, v1}, Landroid/app/Activity;->startActivity(Landroid/content/Intent;)V",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_url_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_url_try_start .. :ahnali_url_try_end} :ahnali_url_fail",
        "    :ahnali_url_fail",
        "    const/4 v0, 0x0",
        "    return v0",
        ".end method",
    ]


def _emit_connectivity_is_connected_method() -> list[str]:
    return [
        ".method public static isConnected(Landroid/app/Activity;)I",
        "    .locals 4",
        "    if-eqz p0, :ahnali_conn_fail",
        "    :ahnali_conn_try_start",
        '    const-string v0, "connectivity"',
        "    invoke-virtual {p0, v0}, Landroid/app/Activity;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;",
        "    move-result-object v1",
        "    check-cast v1, Landroid/net/ConnectivityManager;",
        "    if-eqz v1, :ahnali_conn_fail",
        "    invoke-virtual {v1}, Landroid/net/ConnectivityManager;->getActiveNetworkInfo()Landroid/net/NetworkInfo;",
        "    move-result-object v2",
        "    if-eqz v2, :ahnali_conn_fail",
        "    invoke-virtual {v2}, Landroid/net/NetworkInfo;->isConnected()Z",
        "    move-result v3",
        "    return v3",
        "    :ahnali_conn_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_conn_try_start .. :ahnali_conn_try_end} :ahnali_conn_fail",
        "    :ahnali_conn_fail",
        "    const/4 v0, 0x0",
        "    return v0",
        ".end method",
    ]


def _emit_location_is_enabled_method() -> list[str]:
    return [
        ".method public static isLocationEnabled(Landroid/app/Activity;)I",
        "    .locals 5",
        "    if-eqz p0, :ahnali_loc_fail",
        "    :ahnali_loc_try_start",
        '    const-string v0, "location"',
        "    invoke-virtual {p0, v0}, Landroid/app/Activity;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;",
        "    move-result-object v1",
        "    check-cast v1, Landroid/location/LocationManager;",
        "    if-eqz v1, :ahnali_loc_fail",
        '    const-string v2, "gps"',
        "    invoke-virtual {v1, v2}, Landroid/location/LocationManager;->isProviderEnabled(Ljava/lang/String;)Z",
        "    move-result v3",
        "    if-nez v3, :ahnali_loc_true",
        '    const-string v2, "network"',
        "    invoke-virtual {v1, v2}, Landroid/location/LocationManager;->isProviderEnabled(Ljava/lang/String;)Z",
        "    move-result v4",
        "    return v4",
        "    :ahnali_loc_true",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_loc_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_loc_try_start .. :ahnali_loc_try_end} :ahnali_loc_fail",
        "    :ahnali_loc_fail",
        "    const/4 v0, 0x0",
        "    return v0",
        ".end method",
    ]


def _emit_permission_is_granted_method() -> list[str]:
    return [
        ".method public static isGranted(Landroid/app/Activity;Ljava/lang/String;)I",
        "    .locals 3",
        "    if-eqz p0, :ahnali_perm_fail",
        "    if-eqz p1, :ahnali_perm_fail",
        "    :ahnali_perm_try_start",
        "    invoke-virtual {p0, p1}, Landroid/app/Activity;->checkCallingOrSelfPermission(Ljava/lang/String;)I",
        "    move-result v1",
        "    if-nez v1, :ahnali_perm_fail",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_perm_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_perm_try_start .. :ahnali_perm_try_end} :ahnali_perm_fail",
        "    :ahnali_perm_fail",
        "    const/4 v0, 0x0",
        "    return v0",
        ".end method",
    ]


def _emit_web_set_policy_method() -> list[str]:
    return [
        ".method public static setPolicy(Landroid/app/Activity;IIII)I",
        "    .locals 1",
        "    if-eqz p0, :ahnali_web_policy_fail",
        "    sput p1, Lcom/ahnali/runtime/WebHelper;->sJsEnabled:I",
        "    sput p2, Lcom/ahnali/runtime/WebHelper;->sDomStorage:I",
        "    sput p3, Lcom/ahnali/runtime/WebHelper;->sAllowFileAccess:I",
        "    sput p4, Lcom/ahnali/runtime/WebHelper;->sAllowCleartext:I",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_web_policy_fail",
        "    const/4 v0, 0x0",
        "    return v0",
        ".end method",
    ]


def _emit_web_load_url_method() -> list[str]:
    return [
        ".method public static loadUrl(Landroid/app/Activity;Ljava/lang/String;)I",
        "    .locals 2",
        "    invoke-static {p0, p1}, Lcom/ahnali/runtime/WebHelper;->loadUrlError(Landroid/app/Activity;Ljava/lang/String;)I",
        "    move-result v0",
        "    if-nez v0, :ahnali_web_load_fail",
        "    const/4 v1, 0x1",
        "    return v1",
        "    :ahnali_web_load_fail",
        "    const/4 v1, 0x0",
        "    return v1",
        ".end method",
    ]


def _emit_web_load_url_error_method() -> list[str]:
    return [
        ".method public static loadUrlError(Landroid/app/Activity;Ljava/lang/String;)I",
        "    .locals 8",
        "    if-eqz p0, :ahnali_web_invalid",
        "    if-eqz p1, :ahnali_web_invalid",
        "    sget v0, Lcom/ahnali/runtime/WebHelper;->sAllowCleartext:I",
        "    if-nez v0, :ahnali_web_policy_ok",
        '    const-string v1, "https://"',
        "    invoke-virtual {p1, v1}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z",
        "    move-result v2",
        "    if-nez v2, :ahnali_web_policy_ok",
        "    const/4 v0, 0x2",
        "    return v0",
        "    :ahnali_web_policy_ok",
        "    :ahnali_web_try_start",
        "    new-instance v3, Landroid/webkit/WebView;",
        "    invoke-direct {v3, p0}, Landroid/webkit/WebView;-><init>(Landroid/content/Context;)V",
        "    invoke-virtual {v3}, Landroid/webkit/WebView;->getSettings()Landroid/webkit/WebSettings;",
        "    move-result-object v4",
        "    if-eqz v4, :ahnali_web_runtime_error",
        "    sget v5, Lcom/ahnali/runtime/WebHelper;->sJsEnabled:I",
        "    invoke-virtual {v4, v5}, Landroid/webkit/WebSettings;->setJavaScriptEnabled(Z)V",
        "    sget v6, Lcom/ahnali/runtime/WebHelper;->sDomStorage:I",
        "    invoke-virtual {v4, v6}, Landroid/webkit/WebSettings;->setDomStorageEnabled(Z)V",
        "    sget v7, Lcom/ahnali/runtime/WebHelper;->sAllowFileAccess:I",
        "    invoke-virtual {v4, v7}, Landroid/webkit/WebSettings;->setAllowFileAccess(Z)V",
        "    invoke-virtual {v3, p1}, Landroid/webkit/WebView;->loadUrl(Ljava/lang/String;)V",
        "    new-instance v5, Landroid/app/AlertDialog$Builder;",
        "    invoke-direct {v5, p0}, Landroid/app/AlertDialog$Builder;-><init>(Landroid/content/Context;)V",
        "    invoke-virtual {v5, v3}, Landroid/app/AlertDialog$Builder;->setView(Landroid/view/View;)Landroid/app/AlertDialog$Builder;",
        "    move-result-object v5",
        "    invoke-virtual {v5}, Landroid/app/AlertDialog$Builder;->show()Landroid/app/AlertDialog;",
        "    move-result-object v6",
        "    const/4 v0, 0x0",
        "    return v0",
        "    :ahnali_web_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_web_try_start .. :ahnali_web_try_end} :ahnali_web_exception",
        "    :ahnali_web_invalid",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_web_runtime_error",
        "    const/4 v0, 0x3",
        "    return v0",
        "    :ahnali_web_exception",
        "    const/4 v0, 0x4",
        "    return v0",
        ".end method",
    ]


def _emit_notification_create_channel_method() -> list[str]:
    return [
        ".method public static createChannel(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I",
        "    .locals 7",
        "    if-eqz p0, :ahnali_notify_channel_invalid",
        "    if-eqz p1, :ahnali_notify_channel_invalid",
        "    if-eqz p2, :ahnali_notify_channel_invalid",
        "    :ahnali_notify_channel_try_start",
        '    const-string v1, "notification"',
        "    invoke-virtual {p0, v1}, Landroid/app/Activity;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;",
        "    move-result-object v2",
        "    check-cast v2, Landroid/app/NotificationManager;",
        "    if-eqz v2, :ahnali_notify_channel_error",
        "    sget v3, Landroid/os/Build$VERSION;->SDK_INT:I",
        "    const/16 v4, 0x1a",
        "    if-lt v3, v4, :ahnali_notify_channel_ok",
        "    new-instance v5, Landroid/app/NotificationChannel;",
        "    const/4 v6, 0x3",
        "    invoke-direct {v5, p1, p2, v6}, Landroid/app/NotificationChannel;-><init>(Ljava/lang/String;Ljava/lang/CharSequence;I)V",
        "    invoke-virtual {v2, v5}, Landroid/app/NotificationManager;->createNotificationChannel(Landroid/app/NotificationChannel;)V",
        "    :ahnali_notify_channel_ok",
        "    const/4 v0, 0x0",
        "    return v0",
        "    :ahnali_notify_channel_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_notify_channel_try_start .. :ahnali_notify_channel_try_end} :ahnali_notify_channel_exception",
        "    :ahnali_notify_channel_error",
        "    const/4 v0, 0x3",
        "    return v0",
        "    :ahnali_notify_channel_invalid",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_notify_channel_exception",
        "    const/4 v0, 0x4",
        "    return v0",
        ".end method",
    ]


def _emit_notification_post_method() -> list[str]:
    return [
        ".method public static postNotification(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I",
        "    .locals 2",
        "    invoke-static {p0, p1, p2, p3}, Lcom/ahnali/runtime/NotificationHelper;->postNotificationError(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I",
        "    move-result v0",
        "    if-nez v0, :ahnali_notify_post_fail",
        "    const/4 v1, 0x1",
        "    return v1",
        "    :ahnali_notify_post_fail",
        "    const/4 v1, 0x0",
        "    return v1",
        ".end method",
    ]


def _emit_notification_post_error_method() -> list[str]:
    return [
        ".method public static postNotificationError(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I",
        "    .locals 12",
        "    if-eqz p0, :ahnali_notify_post_invalid",
        "    if-eqz p1, :ahnali_notify_post_invalid",
        "    if-eqz p2, :ahnali_notify_post_invalid",
        "    if-eqz p3, :ahnali_notify_post_invalid",
        "    sget v1, Landroid/os/Build$VERSION;->SDK_INT:I",
        "    const/16 v2, 0x21",
        "    if-lt v1, v2, :ahnali_notify_post_permission_ok",
        '    const-string v3, "android.permission.POST_NOTIFICATIONS"',
        "    invoke-virtual {p0, v3}, Landroid/app/Activity;->checkCallingOrSelfPermission(Ljava/lang/String;)I",
        "    move-result v4",
        "    if-eqz v4, :ahnali_notify_post_permission_ok",
        "    const/4 v0, 0x2",
        "    return v0",
        "    :ahnali_notify_post_permission_ok",
        "    invoke-static {p0, p3, p3}, Lcom/ahnali/runtime/NotificationHelper;->createChannel(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I",
        "    move-result v5",
        "    if-nez v5, :ahnali_notify_post_channel_error",
        "    :ahnali_notify_post_try_start",
        '    const-string v6, "notification"',
        "    invoke-virtual {p0, v6}, Landroid/app/Activity;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;",
        "    move-result-object v7",
        "    check-cast v7, Landroid/app/NotificationManager;",
        "    if-eqz v7, :ahnali_notify_post_runtime_error",
        "    sget v8, Landroid/os/Build$VERSION;->SDK_INT:I",
        "    const/16 v9, 0x1a",
        "    if-lt v8, v9, :ahnali_notify_builder_legacy",
        "    new-instance v10, Landroid/app/Notification$Builder;",
        "    invoke-direct {v10, p0, p3}, Landroid/app/Notification$Builder;-><init>(Landroid/content/Context;Ljava/lang/String;)V",
        "    goto :ahnali_notify_builder_ready",
        "    :ahnali_notify_builder_legacy",
        "    new-instance v10, Landroid/app/Notification$Builder;",
        "    invoke-direct {v10, p0}, Landroid/app/Notification$Builder;-><init>(Landroid/content/Context;)V",
        "    :ahnali_notify_builder_ready",
        "    invoke-virtual {v10, p1}, Landroid/app/Notification$Builder;->setContentTitle(Ljava/lang/CharSequence;)Landroid/app/Notification$Builder;",
        "    move-result-object v10",
        "    invoke-virtual {v10, p2}, Landroid/app/Notification$Builder;->setContentText(Ljava/lang/CharSequence;)Landroid/app/Notification$Builder;",
        "    move-result-object v10",
        "    const v11, 0x1080027",
        "    invoke-virtual {v10, v11}, Landroid/app/Notification$Builder;->setSmallIcon(I)Landroid/app/Notification$Builder;",
        "    move-result-object v10",
        "    const/4 v11, 0x1",
        "    invoke-virtual {v10, v11}, Landroid/app/Notification$Builder;->setAutoCancel(Z)Landroid/app/Notification$Builder;",
        "    move-result-object v10",
        "    invoke-virtual {v10}, Landroid/app/Notification$Builder;->build()Landroid/app/Notification;",
        "    move-result-object v6",
        "    const/16 v8, 0x11",
        "    invoke-virtual {v7, v8, v6}, Landroid/app/NotificationManager;->notify(ILandroid/app/Notification;)V",
        "    const/4 v0, 0x0",
        "    return v0",
        "    :ahnali_notify_post_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_notify_post_try_start .. :ahnali_notify_post_try_end} :ahnali_notify_post_runtime_error",
        "    :ahnali_notify_post_channel_error",
        "    return v5",
        "    :ahnali_notify_post_invalid",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_notify_post_runtime_error",
        "    const/4 v0, 0x4",
        "    return v0",
        ".end method",
    ]


def _emit_clipboard_set_text_method() -> list[str]:
    return [
        ".method public static setText(Landroid/app/Activity;Ljava/lang/String;)I",
        "    .locals 5",
        "    if-eqz p0, :ahnali_clip_set_fail",
        "    if-eqz p1, :ahnali_clip_set_fail",
        "    :ahnali_clip_set_try_start",
        '    const-string v0, "clipboard"',
        "    invoke-virtual {p0, v0}, Landroid/app/Activity;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;",
        "    move-result-object v1",
        "    check-cast v1, Landroid/content/ClipboardManager;",
        "    if-eqz v1, :ahnali_clip_set_fail",
        '    const-string v2, "ahnali_clip"',
        "    invoke-static {v2, p1}, Landroid/content/ClipData;->newPlainText(Ljava/lang/CharSequence;Ljava/lang/CharSequence;)Landroid/content/ClipData;",
        "    move-result-object v3",
        "    invoke-virtual {v1, v3}, Landroid/content/ClipboardManager;->setPrimaryClip(Landroid/content/ClipData;)V",
        "    const/4 v4, 0x1",
        "    return v4",
        "    :ahnali_clip_set_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_clip_set_try_start .. :ahnali_clip_set_try_end} :ahnali_clip_set_fail",
        "    :ahnali_clip_set_fail",
        "    const/4 v0, 0x0",
        "    return v0",
        ".end method",
    ]


def _emit_clipboard_get_text_method() -> list[str]:
    return [
        ".method public static getText(Landroid/app/Activity;Ljava/lang/String;)Ljava/lang/String;",
        "    .locals 8",
        "    if-eqz p0, :ahnali_clip_get_fallback",
        "    :ahnali_clip_get_try_start",
        '    const-string v0, "clipboard"',
        "    invoke-virtual {p0, v0}, Landroid/app/Activity;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;",
        "    move-result-object v1",
        "    check-cast v1, Landroid/content/ClipboardManager;",
        "    if-eqz v1, :ahnali_clip_get_fallback",
        "    invoke-virtual {v1}, Landroid/content/ClipboardManager;->hasPrimaryClip()Z",
        "    move-result v2",
        "    if-eqz v2, :ahnali_clip_get_fallback",
        "    invoke-virtual {v1}, Landroid/content/ClipboardManager;->getPrimaryClip()Landroid/content/ClipData;",
        "    move-result-object v3",
        "    if-eqz v3, :ahnali_clip_get_fallback",
        "    const/4 v4, 0x0",
        "    invoke-virtual {v3, v4}, Landroid/content/ClipData;->getItemAt(I)Landroid/content/ClipData$Item;",
        "    move-result-object v5",
        "    if-eqz v5, :ahnali_clip_get_fallback",
        "    invoke-virtual {v5, p0}, Landroid/content/ClipData$Item;->coerceToText(Landroid/content/Context;)Ljava/lang/CharSequence;",
        "    move-result-object v6",
        "    if-eqz v6, :ahnali_clip_get_fallback",
        "    invoke-virtual {v6}, Ljava/lang/Object;->toString()Ljava/lang/String;",
        "    move-result-object v7",
        "    if-eqz v7, :ahnali_clip_get_fallback",
        "    return-object v7",
        "    :ahnali_clip_get_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_clip_get_try_start .. :ahnali_clip_get_try_end} :ahnali_clip_get_fallback",
        "    :ahnali_clip_get_fallback",
        "    return-object p1",
        ".end method",
    ]


def _emit_share_text_method() -> list[str]:
    return [
        ".method public static shareText(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I",
        "    .locals 2",
        "    invoke-static {p0, p1, p2}, Lcom/ahnali/runtime/ShareHelper;->shareTextError(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I",
        "    move-result v0",
        "    if-nez v0, :ahnali_share_fail",
        "    const/4 v1, 0x1",
        "    return v1",
        "    :ahnali_share_fail",
        "    const/4 v1, 0x0",
        "    return v1",
        ".end method",
    ]


def _emit_share_text_error_method() -> list[str]:
    return [
        ".method public static shareTextError(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I",
        "    .locals 7",
        "    if-eqz p0, :ahnali_share_invalid",
        "    if-eqz p1, :ahnali_share_invalid",
        "    if-eqz p2, :ahnali_share_invalid",
        "    :ahnali_share_try_start",
        "    new-instance v1, Landroid/content/Intent;",
        '    const-string v2, "android.intent.action.SEND"',
        "    invoke-direct {v1, v2}, Landroid/content/Intent;-><init>(Ljava/lang/String;)V",
        '    const-string v3, "text/plain"',
        "    invoke-virtual {v1, v3}, Landroid/content/Intent;->setType(Ljava/lang/String;)Landroid/content/Intent;",
        '    const-string v4, "android.intent.extra.TEXT"',
        "    invoke-virtual {v1, v4, p1}, Landroid/content/Intent;->putExtra(Ljava/lang/String;Ljava/lang/String;)Landroid/content/Intent;",
        "    invoke-static {v1, p2}, Landroid/content/Intent;->createChooser(Landroid/content/Intent;Ljava/lang/CharSequence;)Landroid/content/Intent;",
        "    move-result-object v5",
        "    invoke-virtual {p0, v5}, Landroid/app/Activity;->startActivity(Landroid/content/Intent;)V",
        "    const/4 v0, 0x0",
        "    return v0",
        "    :ahnali_share_try_end",
        "    .catch Landroid/content/ActivityNotFoundException; {:ahnali_share_try_start .. :ahnali_share_try_end} :ahnali_share_not_found",
        "    .catch Ljava/lang/Exception; {:ahnali_share_try_start .. :ahnali_share_try_end} :ahnali_share_exception",
        "    :ahnali_share_invalid",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_share_not_found",
        "    const/4 v0, 0x3",
        "    return v0",
        "    :ahnali_share_exception",
        "    const/4 v0, 0x4",
        "    return v0",
        ".end method",
    ]


def _emit_open_uri_method() -> list[str]:
    return [
        ".method public static openUri(Landroid/app/Activity;Ljava/lang/String;)I",
        "    .locals 2",
        "    invoke-static {p0, p1}, Lcom/ahnali/runtime/ShareHelper;->openUriError(Landroid/app/Activity;Ljava/lang/String;)I",
        "    move-result v0",
        "    if-nez v0, :ahnali_open_uri_fail",
        "    const/4 v1, 0x1",
        "    return v1",
        "    :ahnali_open_uri_fail",
        "    const/4 v1, 0x0",
        "    return v1",
        ".end method",
    ]


def _emit_open_uri_error_method() -> list[str]:
    return [
        ".method public static openUriError(Landroid/app/Activity;Ljava/lang/String;)I",
        "    .locals 5",
        "    if-eqz p0, :ahnali_open_uri_invalid",
        "    if-eqz p1, :ahnali_open_uri_invalid",
        "    :ahnali_open_uri_try_start",
        "    new-instance v1, Landroid/content/Intent;",
        '    const-string v2, "android.intent.action.VIEW"',
        "    invoke-direct {v1, v2}, Landroid/content/Intent;-><init>(Ljava/lang/String;)V",
        "    invoke-static {p1}, Landroid/net/Uri;->parse(Ljava/lang/String;)Landroid/net/Uri;",
        "    move-result-object v3",
        "    invoke-virtual {v1, v3}, Landroid/content/Intent;->setData(Landroid/net/Uri;)Landroid/content/Intent;",
        "    invoke-virtual {p0, v1}, Landroid/app/Activity;->startActivity(Landroid/content/Intent;)V",
        "    const/4 v0, 0x0",
        "    return v0",
        "    :ahnali_open_uri_try_end",
        "    .catch Landroid/content/ActivityNotFoundException; {:ahnali_open_uri_try_start .. :ahnali_open_uri_try_end} :ahnali_open_uri_not_found",
        "    .catch Ljava/lang/Exception; {:ahnali_open_uri_try_start .. :ahnali_open_uri_try_end} :ahnali_open_uri_exception",
        "    :ahnali_open_uri_invalid",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_open_uri_not_found",
        "    const/4 v0, 0x3",
        "    return v0",
        "    :ahnali_open_uri_exception",
        "    const/4 v0, 0x4",
        "    return v0",
        ".end method",
    ]


def _emit_http_get_method() -> list[str]:
    return [
        ".method public static httpGet(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;",
        "    .locals 2",
        "    const/16 v0, 0x1f40",
        "    invoke-static {p0, p1, p2, v0}, Lcom/ahnali/runtime/HttpHelper;->httpGetWithTimeout(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;I)Ljava/lang/String;",
        "    move-result-object v1",
        "    return-object v1",
        ".end method",
    ]


def _emit_http_get_status_method() -> list[str]:
    return [
        ".method public static httpGetStatus(Landroid/app/Activity;Ljava/lang/String;)I",
        "    .locals 2",
        "    const/16 v0, 0x1f40",
        "    invoke-static {p0, p1, v0}, Lcom/ahnali/runtime/HttpHelper;->httpGetStatusWithTimeout(Landroid/app/Activity;Ljava/lang/String;I)I",
        "    move-result v1",
        "    return v1",
        ".end method",
    ]


def _emit_http_get_error_method() -> list[str]:
    return [
        ".method public static httpGetError(Landroid/app/Activity;Ljava/lang/String;)I",
        "    .locals 2",
        "    const/16 v0, 0x1f40",
        "    invoke-static {p0, p1, v0}, Lcom/ahnali/runtime/HttpHelper;->httpGetErrorWithTimeout(Landroid/app/Activity;Ljava/lang/String;I)I",
        "    move-result v1",
        "    return v1",
        ".end method",
    ]


def _emit_http_get_with_timeout_method() -> list[str]:
    return [
        ".method public static httpGetWithTimeout(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;I)Ljava/lang/String;",
        "    .locals 9",
        "    if-eqz p1, :ahnali_http_get_fallback",
        "    move v2, p3",
        "    if-gtz v2, :ahnali_http_get_timeout_ready",
        "    const/16 v2, 0x1f40",
        "    :ahnali_http_get_timeout_ready",
        "    :ahnali_http_get_try_start",
        "    new-instance v0, Ljava/net/URL;",
        "    invoke-direct {v0, p1}, Ljava/net/URL;-><init>(Ljava/lang/String;)V",
        "    invoke-virtual {v0}, Ljava/net/URL;->openConnection()Ljava/net/URLConnection;",
        "    move-result-object v1",
        "    check-cast v1, Ljava/net/HttpURLConnection;",
        "    if-eqz v1, :ahnali_http_get_fallback",
        '    const-string v3, "GET"',
        "    invoke-virtual {v1, v3}, Ljava/net/HttpURLConnection;->setRequestMethod(Ljava/lang/String;)V",
        "    invoke-virtual {v1, v2}, Ljava/net/HttpURLConnection;->setConnectTimeout(I)V",
        "    invoke-virtual {v1, v2}, Ljava/net/HttpURLConnection;->setReadTimeout(I)V",
        "    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->getResponseCode()I",
        "    move-result v3",
        "    const/16 v4, 0xc8",
        "    if-ne v3, v4, :ahnali_http_get_disconnect_fallback",
        "    new-instance v5, Ljava/util/Scanner;",
        "    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->getInputStream()Ljava/io/InputStream;",
        "    move-result-object v6",
        "    invoke-direct {v5, v6}, Ljava/util/Scanner;-><init>(Ljava/io/InputStream;)V",
        '    const-string v6, "\\\\A"',
        "    invoke-virtual {v5, v6}, Ljava/util/Scanner;->useDelimiter(Ljava/lang/String;)Ljava/util/Scanner;",
        "    move-result-object v5",
        "    invoke-virtual {v5}, Ljava/util/Scanner;->hasNext()Z",
        "    move-result v6",
        "    if-eqz v6, :ahnali_http_get_empty_body",
        "    invoke-virtual {v5}, Ljava/util/Scanner;->next()Ljava/lang/String;",
        "    move-result-object v7",
        "    invoke-virtual {v5}, Ljava/util/Scanner;->close()V",
        "    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->disconnect()V",
        "    if-eqz v7, :ahnali_http_get_fallback",
        "    return-object v7",
        "    :ahnali_http_get_empty_body",
        "    invoke-virtual {v5}, Ljava/util/Scanner;->close()V",
        "    :ahnali_http_get_disconnect_fallback",
        "    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->disconnect()V",
        "    :ahnali_http_get_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_http_get_try_start .. :ahnali_http_get_try_end} :ahnali_http_get_fallback",
        "    :ahnali_http_get_fallback",
        "    return-object p2",
        ".end method",
    ]


def _emit_http_get_status_with_timeout_method() -> list[str]:
    return [
        ".method public static httpGetStatusWithTimeout(Landroid/app/Activity;Ljava/lang/String;I)I",
        "    .locals 6",
        "    if-eqz p1, :ahnali_http_status_fail",
        "    move v2, p2",
        "    if-gtz v2, :ahnali_http_status_timeout_ready",
        "    const/16 v2, 0x1f40",
        "    :ahnali_http_status_timeout_ready",
        "    :ahnali_http_status_try_start",
        "    new-instance v0, Ljava/net/URL;",
        "    invoke-direct {v0, p1}, Ljava/net/URL;-><init>(Ljava/lang/String;)V",
        "    invoke-virtual {v0}, Ljava/net/URL;->openConnection()Ljava/net/URLConnection;",
        "    move-result-object v1",
        "    check-cast v1, Ljava/net/HttpURLConnection;",
        "    if-eqz v1, :ahnali_http_status_fail",
        '    const-string v3, "GET"',
        "    invoke-virtual {v1, v3}, Ljava/net/HttpURLConnection;->setRequestMethod(Ljava/lang/String;)V",
        "    invoke-virtual {v1, v2}, Ljava/net/HttpURLConnection;->setConnectTimeout(I)V",
        "    invoke-virtual {v1, v2}, Ljava/net/HttpURLConnection;->setReadTimeout(I)V",
        "    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->getResponseCode()I",
        "    move-result v4",
        "    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->disconnect()V",
        "    return v4",
        "    :ahnali_http_status_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_http_status_try_start .. :ahnali_http_status_try_end} :ahnali_http_status_fail",
        "    :ahnali_http_status_fail",
        "    const/4 v0, -0x1",
        "    return v0",
        ".end method",
    ]


def _emit_http_get_error_with_timeout_method() -> list[str]:
    return [
        ".method public static httpGetErrorWithTimeout(Landroid/app/Activity;Ljava/lang/String;I)I",
        "    .locals 9",
        "    if-eqz p1, :ahnali_http_error_invalid",
        "    move v2, p2",
        "    if-gtz v2, :ahnali_http_error_timeout_ready",
        "    const/16 v2, 0x1f40",
        "    :ahnali_http_error_timeout_ready",
        "    :ahnali_http_error_try_start",
        "    new-instance v0, Ljava/net/URL;",
        "    invoke-direct {v0, p1}, Ljava/net/URL;-><init>(Ljava/lang/String;)V",
        "    invoke-virtual {v0}, Ljava/net/URL;->openConnection()Ljava/net/URLConnection;",
        "    move-result-object v1",
        "    check-cast v1, Ljava/net/HttpURLConnection;",
        "    if-eqz v1, :ahnali_http_error_exception",
        '    const-string v3, "GET"',
        "    invoke-virtual {v1, v3}, Ljava/net/HttpURLConnection;->setRequestMethod(Ljava/lang/String;)V",
        "    invoke-virtual {v1, v2}, Ljava/net/HttpURLConnection;->setConnectTimeout(I)V",
        "    invoke-virtual {v1, v2}, Ljava/net/HttpURLConnection;->setReadTimeout(I)V",
        "    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->getResponseCode()I",
        "    move-result v3",
        "    const/16 v4, 0xc8",
        "    if-ne v3, v4, :ahnali_http_error_status",
        "    new-instance v5, Ljava/util/Scanner;",
        "    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->getInputStream()Ljava/io/InputStream;",
        "    move-result-object v6",
        "    invoke-direct {v5, v6}, Ljava/util/Scanner;-><init>(Ljava/io/InputStream;)V",
        '    const-string v6, "\\\\A"',
        "    invoke-virtual {v5, v6}, Ljava/util/Scanner;->useDelimiter(Ljava/lang/String;)Ljava/util/Scanner;",
        "    move-result-object v5",
        "    invoke-virtual {v5}, Ljava/util/Scanner;->hasNext()Z",
        "    move-result v6",
        "    if-eqz v6, :ahnali_http_error_empty",
        "    invoke-virtual {v5}, Ljava/util/Scanner;->next()Ljava/lang/String;",
        "    move-result-object v7",
        "    invoke-virtual {v5}, Ljava/util/Scanner;->close()V",
        "    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->disconnect()V",
        "    if-eqz v7, :ahnali_http_error_empty_return",
        "    const/4 v0, 0x0",
        "    return v0",
        "    :ahnali_http_error_empty",
        "    invoke-virtual {v5}, Ljava/util/Scanner;->close()V",
        "    :ahnali_http_error_empty_return",
        "    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->disconnect()V",
        "    const/4 v0, 0x4",
        "    return v0",
        "    :ahnali_http_error_status",
        "    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->disconnect()V",
        "    const/4 v0, 0x3",
        "    return v0",
        "    :ahnali_http_error_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_http_error_try_start .. :ahnali_http_error_try_end} :ahnali_http_error_exception",
        "    :ahnali_http_error_invalid",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_http_error_exception",
        "    const/4 v0, 0x2",
        "    return v0",
        ".end method",
    ]


def _emit_http_get_retry_method() -> list[str]:
    return [
        ".method public static httpGetRetry(Landroid/app/Activity;Ljava/lang/String;IILjava/lang/String;)Ljava/lang/String;",
        "    .locals 7",
        "    if-eqz p1, :ahnali_http_retry_fallback",
        "    move v0, p2",
        "    if-gez v0, :ahnali_http_retry_retries_ok",
        "    const/4 v0, 0x0",
        "    :ahnali_http_retry_retries_ok",
        "    move v1, p3",
        "    if-gez v1, :ahnali_http_retry_backoff_ok",
        "    const/4 v1, 0x0",
        "    :ahnali_http_retry_backoff_ok",
        "    :ahnali_http_retry_loop",
        "    invoke-static {p0, p1}, Lcom/ahnali/runtime/HttpHelper;->httpGetError(Landroid/app/Activity;Ljava/lang/String;)I",
        "    move-result v2",
        "    if-nez v2, :ahnali_http_retry_fail_attempt",
        "    invoke-static {p0, p1, p4}, Lcom/ahnali/runtime/HttpHelper;->httpGet(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;",
        "    move-result-object v3",
        "    if-eqz v3, :ahnali_http_retry_fallback",
        "    return-object v3",
        "    :ahnali_http_retry_fail_attempt",
        "    if-lez v0, :ahnali_http_retry_fallback",
        "    if-lez v1, :ahnali_http_retry_after_sleep",
        "    int-to-long v4, v1",
        "    :ahnali_http_retry_sleep_try_start",
        "    invoke-static {v4, v5}, Ljava/lang/Thread;->sleep(J)V",
        "    :ahnali_http_retry_sleep_try_end",
        "    .catch Ljava/lang/InterruptedException; {:ahnali_http_retry_sleep_try_start .. :ahnali_http_retry_sleep_try_end} :ahnali_http_retry_after_sleep",
        "    :ahnali_http_retry_after_sleep",
        "    add-int/lit8 v0, v0, -0x1",
        "    goto :ahnali_http_retry_loop",
        "    :ahnali_http_retry_fallback",
        "    return-object p4",
        ".end method",
    ]


def _emit_http_get_json_field_error_method() -> list[str]:
    return [
        ".method public static httpGetJsonFieldError(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I",
        "    .locals 5",
        "    if-eqz p1, :ahnali_http_json_error_invalid",
        "    if-eqz p2, :ahnali_http_json_error_invalid",
        "    invoke-static {p0, p1}, Lcom/ahnali/runtime/HttpHelper;->httpGetError(Landroid/app/Activity;Ljava/lang/String;)I",
        "    move-result v0",
        "    if-nez v0, :ahnali_http_json_error_passthrough",
        '    const-string v1, ""',
        "    invoke-static {p0, p1, v1}, Lcom/ahnali/runtime/HttpHelper;->httpGet(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;",
        "    move-result-object v2",
        "    if-eqz v2, :ahnali_http_json_error_empty_body",
        "    :ahnali_http_json_error_try_start",
        "    new-instance v3, Lorg/json/JSONObject;",
        "    invoke-direct {v3, v2}, Lorg/json/JSONObject;-><init>(Ljava/lang/String;)V",
        "    invoke-virtual {v3, p2}, Lorg/json/JSONObject;->has(Ljava/lang/String;)Z",
        "    move-result v4",
        "    if-eqz v4, :ahnali_http_json_error_missing_key",
        "    invoke-virtual {v3, p2}, Lorg/json/JSONObject;->isNull(Ljava/lang/String;)Z",
        "    move-result v4",
        "    if-nez v4, :ahnali_http_json_error_missing_key",
        "    const/4 v0, 0x0",
        "    return v0",
        "    :ahnali_http_json_error_try_end",
        "    .catch Lorg/json/JSONException; {:ahnali_http_json_error_try_start .. :ahnali_http_json_error_try_end} :ahnali_http_json_error_malformed",
        "    .catch Ljava/lang/Exception; {:ahnali_http_json_error_try_start .. :ahnali_http_json_error_try_end} :ahnali_http_json_error_exception",
        "    :ahnali_http_json_error_missing_key",
        "    const/4 v0, 0x6",
        "    return v0",
        "    :ahnali_http_json_error_empty_body",
        "    const/4 v0, 0x4",
        "    return v0",
        "    :ahnali_http_json_error_invalid",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_http_json_error_malformed",
        "    const/4 v0, 0x5",
        "    return v0",
        "    :ahnali_http_json_error_exception",
        "    const/4 v0, 0x2",
        "    return v0",
        "    :ahnali_http_json_error_passthrough",
        "    return v0",
        ".end method",
    ]


def _emit_http_get_json_field_method() -> list[str]:
    return [
        ".method public static httpGetJsonField(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;",
        "    .locals 6",
        "    if-eqz p1, :ahnali_http_json_field_fallback",
        "    if-eqz p2, :ahnali_http_json_field_fallback",
        "    invoke-static {p0, p1, p2}, Lcom/ahnali/runtime/HttpHelper;->httpGetJsonFieldError(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I",
        "    move-result v0",
        "    if-nez v0, :ahnali_http_json_field_fallback",
        '    const-string v1, ""',
        "    invoke-static {p0, p1, v1}, Lcom/ahnali/runtime/HttpHelper;->httpGet(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;",
        "    move-result-object v2",
        "    if-eqz v2, :ahnali_http_json_field_fallback",
        "    :ahnali_http_json_field_try_start",
        "    new-instance v3, Lorg/json/JSONObject;",
        "    invoke-direct {v3, v2}, Lorg/json/JSONObject;-><init>(Ljava/lang/String;)V",
        "    invoke-virtual {v3, p2}, Lorg/json/JSONObject;->opt(Ljava/lang/String;)Ljava/lang/Object;",
        "    move-result-object v4",
        "    if-eqz v4, :ahnali_http_json_field_fallback",
        "    invoke-virtual {v4}, Ljava/lang/Object;->toString()Ljava/lang/String;",
        "    move-result-object v5",
        "    if-eqz v5, :ahnali_http_json_field_fallback",
        "    return-object v5",
        "    :ahnali_http_json_field_try_end",
        "    .catch Lorg/json/JSONException; {:ahnali_http_json_field_try_start .. :ahnali_http_json_field_try_end} :ahnali_http_json_field_fallback",
        "    .catch Ljava/lang/Exception; {:ahnali_http_json_field_try_start .. :ahnali_http_json_field_try_end} :ahnali_http_json_field_fallback",
        "    :ahnali_http_json_field_fallback",
        "    return-object p3",
        ".end method",
    ]


def _emit_http_resolve_request_method_method() -> list[str]:
    return [
        ".method private static resolveRequestMethod(Ljava/lang/String;)Ljava/lang/String;",
        "    .locals 2",
        "    if-eqz p0, :ahnali_http_req_method_default",
        "    invoke-virtual {p0}, Ljava/lang/String;->length()I",
        "    move-result v0",
        "    if-lez v0, :ahnali_http_req_method_default",
        '    const-string v0, "GET"',
        "    invoke-virtual {p0, v0}, Ljava/lang/String;->equalsIgnoreCase(Ljava/lang/String;)Z",
        "    move-result v1",
        "    if-nez v1, :ahnali_http_req_method_return",
        '    const-string v0, "POST"',
        "    invoke-virtual {p0, v0}, Ljava/lang/String;->equalsIgnoreCase(Ljava/lang/String;)Z",
        "    move-result v1",
        "    if-eqz v1, :ahnali_http_req_method_invalid",
        "    return-object v0",
        "    :ahnali_http_req_method_default",
        '    const-string v0, "GET"',
        "    :ahnali_http_req_method_return",
        "    return-object v0",
        "    :ahnali_http_req_method_invalid",
        "    const/4 v0, 0x0",
        "    return-object v0",
        ".end method",
    ]


def _emit_http_apply_request_headers_method() -> list[str]:
    return [
        ".method private static applyRequestHeaders(Ljava/net/HttpURLConnection;Ljava/lang/String;)V",
        "    .locals 11",
        "    if-eqz p0, :ahnali_http_apply_headers_return",
        "    if-eqz p1, :ahnali_http_apply_headers_return",
        "    invoke-virtual {p1}, Ljava/lang/String;->length()I",
        "    move-result v0",
        "    if-lez v0, :ahnali_http_apply_headers_return",
        '    const-string v0, "\\n"',
        "    invoke-virtual {p1, v0}, Ljava/lang/String;->split(Ljava/lang/String;)[Ljava/lang/String;",
        "    move-result-object v1",
        "    if-eqz v1, :ahnali_http_apply_headers_return",
        "    array-length v2, v1",
        "    const/4 v3, 0x0",
        "    :ahnali_http_apply_headers_loop",
        "    if-ge v3, v2, :ahnali_http_apply_headers_return",
        "    aget-object v4, v1, v3",
        "    if-eqz v4, :ahnali_http_apply_headers_next",
        "    invoke-virtual {v4}, Ljava/lang/String;->trim()Ljava/lang/String;",
        "    move-result-object v5",
        "    if-eqz v5, :ahnali_http_apply_headers_next",
        "    invoke-virtual {v5}, Ljava/lang/String;->length()I",
        "    move-result v6",
        "    if-lez v6, :ahnali_http_apply_headers_next",
        "    const/16 v7, 0x3a",
        "    invoke-virtual {v5, v7}, Ljava/lang/String;->indexOf(I)I",
        "    move-result v7",
        "    if-lez v7, :ahnali_http_apply_headers_next",
        "    const/4 v10, 0x0",
        "    invoke-virtual {v5, v10, v7}, Ljava/lang/String;->substring(II)Ljava/lang/String;",
        "    move-result-object v8",
        "    if-eqz v8, :ahnali_http_apply_headers_next",
        "    invoke-virtual {v8}, Ljava/lang/String;->trim()Ljava/lang/String;",
        "    move-result-object v8",
        "    if-eqz v8, :ahnali_http_apply_headers_next",
        "    invoke-virtual {v8}, Ljava/lang/String;->length()I",
        "    move-result v10",
        "    if-lez v10, :ahnali_http_apply_headers_next",
        "    add-int/lit8 v10, v7, 0x1",
        "    invoke-virtual {v5, v10}, Ljava/lang/String;->substring(I)Ljava/lang/String;",
        "    move-result-object v9",
        "    if-eqz v9, :ahnali_http_apply_headers_next",
        "    invoke-virtual {v9}, Ljava/lang/String;->trim()Ljava/lang/String;",
        "    move-result-object v9",
        "    invoke-virtual {p0, v8, v9}, Ljava/net/HttpURLConnection;->setRequestProperty(Ljava/lang/String;Ljava/lang/String;)V",
        "    :ahnali_http_apply_headers_next",
        "    add-int/lit8 v3, v3, 0x1",
        "    goto :ahnali_http_apply_headers_loop",
        "    :ahnali_http_apply_headers_return",
        "    return-void",
        ".end method",
    ]


def _emit_http_apply_request_body_method() -> list[str]:
    return [
        ".method private static applyRequestBody(Ljava/net/HttpURLConnection;Ljava/lang/String;Ljava/lang/String;)V",
        "    .locals 6",
        "    if-eqz p0, :ahnali_http_apply_body_return",
        "    if-eqz p1, :ahnali_http_apply_body_return",
        '    const-string v0, "POST"',
        "    invoke-virtual {p1, v0}, Ljava/lang/String;->equalsIgnoreCase(Ljava/lang/String;)Z",
        "    move-result v1",
        "    if-eqz v1, :ahnali_http_apply_body_return",
        "    const/4 v1, 0x1",
        "    invoke-virtual {p0, v1}, Ljava/net/HttpURLConnection;->setDoOutput(Z)V",
        "    if-nez p2, :ahnali_http_apply_body_ready",
        '    const-string p2, ""',
        "    :ahnali_http_apply_body_ready",
        '    const-string v2, "UTF-8"',
        "    invoke-virtual {p2, v2}, Ljava/lang/String;->getBytes(Ljava/lang/String;)[B",
        "    move-result-object v3",
        "    if-eqz v3, :ahnali_http_apply_body_return",
        "    array-length v4, v3",
        "    invoke-virtual {p0, v4}, Ljava/net/HttpURLConnection;->setFixedLengthStreamingMode(I)V",
        "    invoke-virtual {p0}, Ljava/net/HttpURLConnection;->getOutputStream()Ljava/io/OutputStream;",
        "    move-result-object v5",
        "    if-eqz v5, :ahnali_http_apply_body_return",
        "    invoke-virtual {v5, v3}, Ljava/io/OutputStream;->write([B)V",
        "    invoke-virtual {v5}, Ljava/io/OutputStream;->flush()V",
        "    invoke-virtual {v5}, Ljava/io/OutputStream;->close()V",
        "    :ahnali_http_apply_body_return",
        "    return-void",
        ".end method",
    ]


def _emit_http_request_with_timeout_method() -> list[str]:
    return [
        ".method public static httpRequestWithTimeout(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;I)Ljava/lang/String;",
        "    .locals 9",
        "    if-eqz p1, :ahnali_http_req_fallback",
        "    move v2, p6",
        "    if-gtz v2, :ahnali_http_req_timeout_ready",
        "    const/16 v2, 0x1f40",
        "    :ahnali_http_req_timeout_ready",
        "    invoke-static {p2}, Lcom/ahnali/runtime/HttpHelper;->resolveRequestMethod(Ljava/lang/String;)Ljava/lang/String;",
        "    move-result-object v3",
        "    if-eqz v3, :ahnali_http_req_fallback",
        "    :ahnali_http_req_try_start",
        "    new-instance v0, Ljava/net/URL;",
        "    invoke-direct {v0, p1}, Ljava/net/URL;-><init>(Ljava/lang/String;)V",
        "    invoke-virtual {v0}, Ljava/net/URL;->openConnection()Ljava/net/URLConnection;",
        "    move-result-object v1",
        "    check-cast v1, Ljava/net/HttpURLConnection;",
        "    if-eqz v1, :ahnali_http_req_fallback",
        "    invoke-virtual {v1, v3}, Ljava/net/HttpURLConnection;->setRequestMethod(Ljava/lang/String;)V",
        "    invoke-virtual {v1, v2}, Ljava/net/HttpURLConnection;->setConnectTimeout(I)V",
        "    invoke-virtual {v1, v2}, Ljava/net/HttpURLConnection;->setReadTimeout(I)V",
        "    invoke-static {v1, p3}, Lcom/ahnali/runtime/HttpHelper;->applyRequestHeaders(Ljava/net/HttpURLConnection;Ljava/lang/String;)V",
        "    invoke-static {v1, v3, p4}, Lcom/ahnali/runtime/HttpHelper;->applyRequestBody(Ljava/net/HttpURLConnection;Ljava/lang/String;Ljava/lang/String;)V",
        "    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->getResponseCode()I",
        "    move-result v4",
        "    const/16 v5, 0xc8",
        "    if-ne v4, v5, :ahnali_http_req_disconnect_fallback",
        "    new-instance v6, Ljava/util/Scanner;",
        "    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->getInputStream()Ljava/io/InputStream;",
        "    move-result-object v7",
        "    invoke-direct {v6, v7}, Ljava/util/Scanner;-><init>(Ljava/io/InputStream;)V",
        '    const-string v7, "\\\\A"',
        "    invoke-virtual {v6, v7}, Ljava/util/Scanner;->useDelimiter(Ljava/lang/String;)Ljava/util/Scanner;",
        "    move-result-object v6",
        "    invoke-virtual {v6}, Ljava/util/Scanner;->hasNext()Z",
        "    move-result v7",
        "    if-eqz v7, :ahnali_http_req_empty_body",
        "    invoke-virtual {v6}, Ljava/util/Scanner;->next()Ljava/lang/String;",
        "    move-result-object v8",
        "    invoke-virtual {v6}, Ljava/util/Scanner;->close()V",
        "    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->disconnect()V",
        "    if-eqz v8, :ahnali_http_req_fallback",
        "    return-object v8",
        "    :ahnali_http_req_empty_body",
        "    invoke-virtual {v6}, Ljava/util/Scanner;->close()V",
        "    :ahnali_http_req_disconnect_fallback",
        "    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->disconnect()V",
        "    :ahnali_http_req_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_http_req_try_start .. :ahnali_http_req_try_end} :ahnali_http_req_fallback",
        "    :ahnali_http_req_fallback",
        "    return-object p5",
        ".end method",
    ]


def _emit_http_request_status_with_timeout_method() -> list[str]:
    return [
        ".method public static httpRequestStatusWithTimeout(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;I)I",
        "    .locals 7",
        "    if-eqz p1, :ahnali_http_req_status_fail",
        "    move v2, p5",
        "    if-gtz v2, :ahnali_http_req_status_timeout_ready",
        "    const/16 v2, 0x1f40",
        "    :ahnali_http_req_status_timeout_ready",
        "    invoke-static {p2}, Lcom/ahnali/runtime/HttpHelper;->resolveRequestMethod(Ljava/lang/String;)Ljava/lang/String;",
        "    move-result-object v3",
        "    if-eqz v3, :ahnali_http_req_status_fail",
        "    :ahnali_http_req_status_try_start",
        "    new-instance v0, Ljava/net/URL;",
        "    invoke-direct {v0, p1}, Ljava/net/URL;-><init>(Ljava/lang/String;)V",
        "    invoke-virtual {v0}, Ljava/net/URL;->openConnection()Ljava/net/URLConnection;",
        "    move-result-object v1",
        "    check-cast v1, Ljava/net/HttpURLConnection;",
        "    if-eqz v1, :ahnali_http_req_status_fail",
        "    invoke-virtual {v1, v3}, Ljava/net/HttpURLConnection;->setRequestMethod(Ljava/lang/String;)V",
        "    invoke-virtual {v1, v2}, Ljava/net/HttpURLConnection;->setConnectTimeout(I)V",
        "    invoke-virtual {v1, v2}, Ljava/net/HttpURLConnection;->setReadTimeout(I)V",
        "    invoke-static {v1, p3}, Lcom/ahnali/runtime/HttpHelper;->applyRequestHeaders(Ljava/net/HttpURLConnection;Ljava/lang/String;)V",
        "    invoke-static {v1, v3, p4}, Lcom/ahnali/runtime/HttpHelper;->applyRequestBody(Ljava/net/HttpURLConnection;Ljava/lang/String;Ljava/lang/String;)V",
        "    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->getResponseCode()I",
        "    move-result v4",
        "    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->disconnect()V",
        "    return v4",
        "    :ahnali_http_req_status_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_http_req_status_try_start .. :ahnali_http_req_status_try_end} :ahnali_http_req_status_fail",
        "    :ahnali_http_req_status_fail",
        "    const/4 v0, -0x1",
        "    return v0",
        ".end method",
    ]


def _emit_http_request_error_with_timeout_method() -> list[str]:
    return [
        ".method public static httpRequestErrorWithTimeout(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;I)I",
        "    .locals 9",
        "    if-eqz p1, :ahnali_http_req_error_invalid",
        "    move v2, p5",
        "    if-gtz v2, :ahnali_http_req_error_timeout_ready",
        "    const/16 v2, 0x1f40",
        "    :ahnali_http_req_error_timeout_ready",
        "    invoke-static {p2}, Lcom/ahnali/runtime/HttpHelper;->resolveRequestMethod(Ljava/lang/String;)Ljava/lang/String;",
        "    move-result-object v3",
        "    if-eqz v3, :ahnali_http_req_error_invalid",
        "    :ahnali_http_req_error_try_start",
        "    new-instance v0, Ljava/net/URL;",
        "    invoke-direct {v0, p1}, Ljava/net/URL;-><init>(Ljava/lang/String;)V",
        "    invoke-virtual {v0}, Ljava/net/URL;->openConnection()Ljava/net/URLConnection;",
        "    move-result-object v1",
        "    check-cast v1, Ljava/net/HttpURLConnection;",
        "    if-eqz v1, :ahnali_http_req_error_exception",
        "    invoke-virtual {v1, v3}, Ljava/net/HttpURLConnection;->setRequestMethod(Ljava/lang/String;)V",
        "    invoke-virtual {v1, v2}, Ljava/net/HttpURLConnection;->setConnectTimeout(I)V",
        "    invoke-virtual {v1, v2}, Ljava/net/HttpURLConnection;->setReadTimeout(I)V",
        "    invoke-static {v1, p3}, Lcom/ahnali/runtime/HttpHelper;->applyRequestHeaders(Ljava/net/HttpURLConnection;Ljava/lang/String;)V",
        "    invoke-static {v1, v3, p4}, Lcom/ahnali/runtime/HttpHelper;->applyRequestBody(Ljava/net/HttpURLConnection;Ljava/lang/String;Ljava/lang/String;)V",
        "    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->getResponseCode()I",
        "    move-result v4",
        "    const/16 v5, 0xc8",
        "    if-ne v4, v5, :ahnali_http_req_error_status",
        "    new-instance v6, Ljava/util/Scanner;",
        "    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->getInputStream()Ljava/io/InputStream;",
        "    move-result-object v7",
        "    invoke-direct {v6, v7}, Ljava/util/Scanner;-><init>(Ljava/io/InputStream;)V",
        '    const-string v7, "\\\\A"',
        "    invoke-virtual {v6, v7}, Ljava/util/Scanner;->useDelimiter(Ljava/lang/String;)Ljava/util/Scanner;",
        "    move-result-object v6",
        "    invoke-virtual {v6}, Ljava/util/Scanner;->hasNext()Z",
        "    move-result v7",
        "    if-eqz v7, :ahnali_http_req_error_empty",
        "    invoke-virtual {v6}, Ljava/util/Scanner;->next()Ljava/lang/String;",
        "    move-result-object v8",
        "    invoke-virtual {v6}, Ljava/util/Scanner;->close()V",
        "    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->disconnect()V",
        "    if-eqz v8, :ahnali_http_req_error_empty_return",
        "    const/4 v0, 0x0",
        "    return v0",
        "    :ahnali_http_req_error_empty",
        "    invoke-virtual {v6}, Ljava/util/Scanner;->close()V",
        "    :ahnali_http_req_error_empty_return",
        "    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->disconnect()V",
        "    const/4 v0, 0x4",
        "    return v0",
        "    :ahnali_http_req_error_status",
        "    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->disconnect()V",
        "    const/4 v0, 0x3",
        "    return v0",
        "    :ahnali_http_req_error_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_http_req_error_try_start .. :ahnali_http_req_error_try_end} :ahnali_http_req_error_exception",
        "    :ahnali_http_req_error_invalid",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_http_req_error_exception",
        "    const/4 v0, 0x2",
        "    return v0",
        ".end method",
    ]


def _emit_http_ensure_async_store_method() -> list[str]:
    return [
        ".method private static ensureAsyncStores()V",
        "    .locals 1",
        "    sget-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncCancelByToken:Landroid/util/SparseIntArray;",
        "    if-nez v0, :ahnali_async_store_progress",
        "    new-instance v0, Landroid/util/SparseIntArray;",
        "    invoke-direct {v0}, Landroid/util/SparseIntArray;-><init>()V",
        "    sput-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncCancelByToken:Landroid/util/SparseIntArray;",
        "    :ahnali_async_store_progress",
        "    sget-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncProgressByToken:Landroid/util/SparseIntArray;",
        "    if-nez v0, :ahnali_async_store_error",
        "    new-instance v0, Landroid/util/SparseIntArray;",
        "    invoke-direct {v0}, Landroid/util/SparseIntArray;-><init>()V",
        "    sput-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncProgressByToken:Landroid/util/SparseIntArray;",
        "    :ahnali_async_store_error",
        "    sget-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncErrorByToken:Landroid/util/SparseIntArray;",
        "    if-nez v0, :ahnali_async_store_status",
        "    new-instance v0, Landroid/util/SparseIntArray;",
        "    invoke-direct {v0}, Landroid/util/SparseIntArray;-><init>()V",
        "    sput-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncErrorByToken:Landroid/util/SparseIntArray;",
        "    :ahnali_async_store_status",
        "    sget-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncStatusByToken:Landroid/util/SparseIntArray;",
        "    if-nez v0, :ahnali_async_store_body",
        "    new-instance v0, Landroid/util/SparseIntArray;",
        "    invoke-direct {v0}, Landroid/util/SparseIntArray;-><init>()V",
        "    sput-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncStatusByToken:Landroid/util/SparseIntArray;",
        "    :ahnali_async_store_body",
        "    sget-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncBodyByToken:Ljava/util/HashMap;",
        "    if-nez v0, :ahnali_async_store_done",
        "    new-instance v0, Ljava/util/HashMap;",
        "    invoke-direct {v0}, Ljava/util/HashMap;-><init>()V",
        "    sput-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncBodyByToken:Ljava/util/HashMap;",
        "    :ahnali_async_store_done",
        "    return-void",
        ".end method",
    ]


def _emit_http_init_async_token_method() -> list[str]:
    return [
        ".method private static initAsyncToken(I)V",
        "    .locals 3",
        "    if-lez p0, :ahnali_async_init_return",
        "    invoke-static {}, Lcom/ahnali/runtime/HttpHelper;->ensureAsyncStores()V",
        "    sget-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncCancelByToken:Landroid/util/SparseIntArray;",
        "    const/4 v1, 0x0",
        "    invoke-virtual {v0, p0, v1}, Landroid/util/SparseIntArray;->put(II)V",
        "    sget-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncProgressByToken:Landroid/util/SparseIntArray;",
        "    invoke-virtual {v0, p0, v1}, Landroid/util/SparseIntArray;->put(II)V",
        "    sget-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncErrorByToken:Landroid/util/SparseIntArray;",
        "    invoke-virtual {v0, p0, v1}, Landroid/util/SparseIntArray;->put(II)V",
        "    sget-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncStatusByToken:Landroid/util/SparseIntArray;",
        "    const/4 v1, -0x1",
        "    invoke-virtual {v0, p0, v1}, Landroid/util/SparseIntArray;->put(II)V",
        "    sget-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncBodyByToken:Ljava/util/HashMap;",
        "    invoke-static {p0}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;",
        "    move-result-object v1",
        "    const/4 v2, 0x0",
        "    invoke-virtual {v0, v1, v2}, Ljava/util/HashMap;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;",
        "    :ahnali_async_init_return",
        "    return-void",
        ".end method",
    ]


def _emit_http_get_current_async_token_method() -> list[str]:
    return [
        ".method public static getCurrentAsyncToken()I",
        "    .locals 1",
        "    sget v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncToken:I",
        "    return v0",
        ".end method",
    ]


def _emit_http_next_async_token_method() -> list[str]:
    return [
        ".method public static nextAsyncToken()I",
        "    .locals 2",
        "    invoke-static {}, Lcom/ahnali/runtime/HttpHelper;->ensureAsyncStores()V",
        "    sget v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncNextToken:I",
        "    add-int/lit8 v0, v0, 0x1",
        "    if-gtz v0, :ahnali_http_async_token_store",
        "    const/4 v0, 0x1",
        "    :ahnali_http_async_token_store",
        "    sput v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncNextToken:I",
        "    sput v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncToken:I",
        "    invoke-static {v0}, Lcom/ahnali/runtime/HttpHelper;->initAsyncToken(I)V",
        "    return v0",
        ".end method",
    ]


def _emit_http_start_async_method() -> list[str]:
    return [
        ".method public static startAsync(Ljava/lang/Runnable;)I",
        "    .locals 2",
        "    if-eqz p0, :ahnali_http_async_fail",
        "    invoke-static {}, Lcom/ahnali/runtime/HttpHelper;->nextAsyncToken()I",
        "    move-result v0",
        "    invoke-static {v0, p0}, Lcom/ahnali/runtime/HttpHelper;->startAsyncWithToken(ILjava/lang/Runnable;)I",
        "    move-result v1",
        "    return v1",
        "    :ahnali_http_async_fail",
        "    const/4 v0, 0x0",
        "    return v0",
        ".end method",
    ]


def _emit_http_start_async_with_token_method() -> list[str]:
    return [
        ".method public static startAsyncWithToken(ILjava/lang/Runnable;)I",
        "    .locals 2",
        "    if-lez p0, :ahnali_http_async_fail",
        "    if-eqz p1, :ahnali_http_async_fail",
        "    invoke-static {}, Lcom/ahnali/runtime/HttpHelper;->ensureAsyncStores()V",
        "    invoke-static {p0}, Lcom/ahnali/runtime/HttpHelper;->initAsyncToken(I)V",
        "    :ahnali_http_async_try_start",
        "    new-instance v0, Ljava/lang/Thread;",
        "    invoke-direct {v0, p1}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;)V",
        "    invoke-virtual {v0}, Ljava/lang/Thread;->start()V",
        "    return p0",
        "    :ahnali_http_async_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_http_async_try_start .. :ahnali_http_async_try_end} :ahnali_http_async_fail",
        "    :ahnali_http_async_fail",
        "    const/4 v0, 0x0",
        "    return v0",
        ".end method",
    ]


def _emit_http_cancel_async_method() -> list[str]:
    return [
        ".method public static cancelAsync(I)I",
        "    .locals 3",
        "    if-lez p0, :ahnali_http_cancel_fail",
        "    invoke-static {}, Lcom/ahnali/runtime/HttpHelper;->ensureAsyncStores()V",
        "    sget-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncCancelByToken:Landroid/util/SparseIntArray;",
        "    const/4 v1, -0x1",
        "    invoke-virtual {v0, p0, v1}, Landroid/util/SparseIntArray;->get(II)I",
        "    move-result v2",
        "    if-eq v2, v1, :ahnali_http_cancel_fail",
        "    const/4 v1, 0x1",
        "    invoke-virtual {v0, p0, v1}, Landroid/util/SparseIntArray;->put(II)V",
        "    return v1",
        "    :ahnali_http_cancel_fail",
        "    const/4 v0, 0x0",
        "    return v0",
        ".end method",
        "",
        ".method public static cancelAsync()I",
        "    .locals 1",
        "    invoke-static {}, Lcom/ahnali/runtime/HttpHelper;->getCurrentAsyncToken()I",
        "    move-result v0",
        "    invoke-static {v0}, Lcom/ahnali/runtime/HttpHelper;->cancelAsync(I)I",
        "    move-result v0",
        "    return v0",
        ".end method",
    ]


def _emit_http_should_cancel_method() -> list[str]:
    return [
        ".method public static shouldCancel(I)I",
        "    .locals 2",
        "    if-lez p0, :ahnali_http_should_cancel_true",
        "    invoke-static {}, Lcom/ahnali/runtime/HttpHelper;->ensureAsyncStores()V",
        "    sget-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncCancelByToken:Landroid/util/SparseIntArray;",
        "    const/4 v1, 0x1",
        "    invoke-virtual {v0, p0, v1}, Landroid/util/SparseIntArray;->get(II)I",
        "    move-result v0",
        "    return v0",
        "    :ahnali_http_should_cancel_true",
        "    const/4 v0, 0x1",
        "    return v0",
        ".end method",
        "",
        ".method public static shouldCancel()I",
        "    .locals 1",
        "    invoke-static {}, Lcom/ahnali/runtime/HttpHelper;->getCurrentAsyncToken()I",
        "    move-result v0",
        "    invoke-static {v0}, Lcom/ahnali/runtime/HttpHelper;->shouldCancel(I)I",
        "    move-result v0",
        "    return v0",
        ".end method",
    ]


def _emit_http_set_async_progress_method() -> list[str]:
    return [
        ".method public static setAsyncProgress(II)V",
        "    .locals 5",
        "    if-lez p0, :ahnali_http_progress_return",
        "    invoke-static {}, Lcom/ahnali/runtime/HttpHelper;->ensureAsyncStores()V",
        "    sget-object v2, Lcom/ahnali/runtime/HttpHelper;->sAsyncCancelByToken:Landroid/util/SparseIntArray;",
        "    const/4 v3, -0x1",
        "    invoke-virtual {v2, p0, v3}, Landroid/util/SparseIntArray;->get(II)I",
        "    move-result v4",
        "    if-eq v4, v3, :ahnali_http_progress_return",
        "    move v0, p1",
        "    if-gez v0, :ahnali_http_progress_non_negative",
        "    const/4 v0, 0x0",
        "    :ahnali_http_progress_non_negative",
        "    const/16 v1, 0x64",
        "    if-le v0, v1, :ahnali_http_progress_store",
        "    move v0, v1",
        "    :ahnali_http_progress_store",
        "    sget-object v2, Lcom/ahnali/runtime/HttpHelper;->sAsyncProgressByToken:Landroid/util/SparseIntArray;",
        "    invoke-virtual {v2, p0, v0}, Landroid/util/SparseIntArray;->put(II)V",
        "    :ahnali_http_progress_return",
        "    return-void",
        ".end method",
        "",
        ".method public static setAsyncProgress(I)V",
        "    .locals 1",
        "    invoke-static {}, Lcom/ahnali/runtime/HttpHelper;->getCurrentAsyncToken()I",
        "    move-result v0",
        "    invoke-static {v0, p0}, Lcom/ahnali/runtime/HttpHelper;->setAsyncProgress(II)V",
        "    return-void",
        ".end method",
    ]


def _emit_http_get_async_progress_method() -> list[str]:
    return [
        ".method public static getAsyncProgress(I)I",
        "    .locals 4",
        "    if-lez p0, :ahnali_http_progress_fail",
        "    invoke-static {}, Lcom/ahnali/runtime/HttpHelper;->ensureAsyncStores()V",
        "    sget-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncCancelByToken:Landroid/util/SparseIntArray;",
        "    const/4 v1, -0x1",
        "    invoke-virtual {v0, p0, v1}, Landroid/util/SparseIntArray;->get(II)I",
        "    move-result v2",
        "    if-eq v2, v1, :ahnali_http_progress_fail",
        "    sget-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncProgressByToken:Landroid/util/SparseIntArray;",
        "    const/4 v1, 0x0",
        "    invoke-virtual {v0, p0, v1}, Landroid/util/SparseIntArray;->get(II)I",
        "    move-result v0",
        "    return v0",
        "    :ahnali_http_progress_fail",
        "    const/4 v0, 0x0",
        "    return v0",
        ".end method",
        "",
        ".method public static getAsyncProgress()I",
        "    .locals 1",
        "    invoke-static {}, Lcom/ahnali/runtime/HttpHelper;->getCurrentAsyncToken()I",
        "    move-result v0",
        "    invoke-static {v0}, Lcom/ahnali/runtime/HttpHelper;->getAsyncProgress(I)I",
        "    move-result v0",
        "    return v0",
        ".end method",
    ]


def _emit_http_set_async_error_method() -> list[str]:
    return [
        ".method public static setAsyncError(II)V",
        "    .locals 4",
        "    if-lez p0, :ahnali_http_error_return",
        "    invoke-static {}, Lcom/ahnali/runtime/HttpHelper;->ensureAsyncStores()V",
        "    sget-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncCancelByToken:Landroid/util/SparseIntArray;",
        "    const/4 v1, -0x1",
        "    invoke-virtual {v0, p0, v1}, Landroid/util/SparseIntArray;->get(II)I",
        "    move-result v2",
        "    if-eq v2, v1, :ahnali_http_error_return",
        "    sget-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncErrorByToken:Landroid/util/SparseIntArray;",
        "    invoke-virtual {v0, p0, p1}, Landroid/util/SparseIntArray;->put(II)V",
        "    :ahnali_http_error_return",
        "    return-void",
        ".end method",
        "",
        ".method public static setAsyncError(I)V",
        "    .locals 1",
        "    invoke-static {}, Lcom/ahnali/runtime/HttpHelper;->getCurrentAsyncToken()I",
        "    move-result v0",
        "    invoke-static {v0, p0}, Lcom/ahnali/runtime/HttpHelper;->setAsyncError(II)V",
        "    return-void",
        ".end method",
    ]


def _emit_http_get_async_error_method() -> list[str]:
    return [
        ".method public static getAsyncError(I)I",
        "    .locals 4",
        "    if-lez p0, :ahnali_http_error_token_fail",
        "    invoke-static {}, Lcom/ahnali/runtime/HttpHelper;->ensureAsyncStores()V",
        "    sget-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncCancelByToken:Landroid/util/SparseIntArray;",
        "    const/4 v1, -0x1",
        "    invoke-virtual {v0, p0, v1}, Landroid/util/SparseIntArray;->get(II)I",
        "    move-result v2",
        "    if-eq v2, v1, :ahnali_http_error_token_fail",
        "    sget-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncErrorByToken:Landroid/util/SparseIntArray;",
        "    const/4 v1, 0x0",
        "    invoke-virtual {v0, p0, v1}, Landroid/util/SparseIntArray;->get(II)I",
        "    move-result v0",
        "    return v0",
        "    :ahnali_http_error_token_fail",
        "    const/16 v0, 0x8",
        "    return v0",
        ".end method",
        "",
        ".method public static getAsyncError()I",
        "    .locals 1",
        "    invoke-static {}, Lcom/ahnali/runtime/HttpHelper;->getCurrentAsyncToken()I",
        "    move-result v0",
        "    invoke-static {v0}, Lcom/ahnali/runtime/HttpHelper;->getAsyncError(I)I",
        "    move-result v0",
        "    return v0",
        ".end method",
    ]


def _emit_http_set_async_status_method() -> list[str]:
    return [
        ".method public static setAsyncStatus(II)V",
        "    .locals 4",
        "    if-lez p0, :ahnali_http_status_return",
        "    invoke-static {}, Lcom/ahnali/runtime/HttpHelper;->ensureAsyncStores()V",
        "    sget-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncCancelByToken:Landroid/util/SparseIntArray;",
        "    const/4 v1, -0x1",
        "    invoke-virtual {v0, p0, v1}, Landroid/util/SparseIntArray;->get(II)I",
        "    move-result v2",
        "    if-eq v2, v1, :ahnali_http_status_return",
        "    sget-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncStatusByToken:Landroid/util/SparseIntArray;",
        "    invoke-virtual {v0, p0, p1}, Landroid/util/SparseIntArray;->put(II)V",
        "    :ahnali_http_status_return",
        "    return-void",
        ".end method",
    ]


def _emit_http_get_async_status_method() -> list[str]:
    return [
        ".method public static getAsyncStatus(I)I",
        "    .locals 4",
        "    if-lez p0, :ahnali_http_status_fail",
        "    invoke-static {}, Lcom/ahnali/runtime/HttpHelper;->ensureAsyncStores()V",
        "    sget-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncCancelByToken:Landroid/util/SparseIntArray;",
        "    const/4 v1, -0x1",
        "    invoke-virtual {v0, p0, v1}, Landroid/util/SparseIntArray;->get(II)I",
        "    move-result v2",
        "    if-eq v2, v1, :ahnali_http_status_fail",
        "    sget-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncStatusByToken:Landroid/util/SparseIntArray;",
        "    const/4 v1, -0x1",
        "    invoke-virtual {v0, p0, v1}, Landroid/util/SparseIntArray;->get(II)I",
        "    move-result v0",
        "    return v0",
        "    :ahnali_http_status_fail",
        "    const/4 v0, -0x1",
        "    return v0",
        ".end method",
    ]


def _emit_http_set_async_body_method() -> list[str]:
    return [
        ".method public static setAsyncBody(ILjava/lang/String;)V",
        "    .locals 4",
        "    if-lez p0, :ahnali_http_body_return",
        "    invoke-static {}, Lcom/ahnali/runtime/HttpHelper;->ensureAsyncStores()V",
        "    sget-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncCancelByToken:Landroid/util/SparseIntArray;",
        "    const/4 v1, -0x1",
        "    invoke-virtual {v0, p0, v1}, Landroid/util/SparseIntArray;->get(II)I",
        "    move-result v2",
        "    if-eq v2, v1, :ahnali_http_body_return",
        "    sget-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncBodyByToken:Ljava/util/HashMap;",
        "    invoke-static {p0}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;",
        "    move-result-object v1",
        "    invoke-virtual {v0, v1, p1}, Ljava/util/HashMap;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;",
        "    :ahnali_http_body_return",
        "    return-void",
        ".end method",
    ]


def _emit_http_get_async_body_method() -> list[str]:
    return [
        ".method public static getAsyncBody(ILjava/lang/String;)Ljava/lang/String;",
        "    .locals 5",
        "    if-lez p0, :ahnali_http_body_fallback",
        "    invoke-static {}, Lcom/ahnali/runtime/HttpHelper;->ensureAsyncStores()V",
        "    sget-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncCancelByToken:Landroid/util/SparseIntArray;",
        "    const/4 v1, -0x1",
        "    invoke-virtual {v0, p0, v1}, Landroid/util/SparseIntArray;->get(II)I",
        "    move-result v2",
        "    if-eq v2, v1, :ahnali_http_body_fallback",
        "    sget-object v0, Lcom/ahnali/runtime/HttpHelper;->sAsyncBodyByToken:Ljava/util/HashMap;",
        "    invoke-static {p0}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;",
        "    move-result-object v1",
        "    invoke-virtual {v0, v1}, Ljava/util/HashMap;->get(Ljava/lang/Object;)Ljava/lang/Object;",
        "    move-result-object v3",
        "    if-eqz v3, :ahnali_http_body_fallback",
        "    check-cast v3, Ljava/lang/String;",
        "    return-object v3",
        "    :ahnali_http_body_fallback",
        "    return-object p1",
        ".end method",
    ]


def _emit_http_get_async_json_field_error_method() -> list[str]:
    return [
        ".method public static getAsyncJsonFieldError(ILjava/lang/String;)I",
        "    .locals 6",
        "    if-eqz p1, :ahnali_http_async_json_error_invalid",
        "    invoke-static {p0}, Lcom/ahnali/runtime/HttpHelper;->getAsyncError(I)I",
        "    move-result v0",
        "    if-eqz v0, :ahnali_http_async_json_error_body",
        "    return v0",
        "    :ahnali_http_async_json_error_body",
        '    const-string v1, ""',
        "    invoke-static {p0, v1}, Lcom/ahnali/runtime/HttpHelper;->getAsyncBody(ILjava/lang/String;)Ljava/lang/String;",
        "    move-result-object v2",
        "    if-eqz v2, :ahnali_http_async_json_error_empty",
        "    invoke-virtual {v2}, Ljava/lang/String;->length()I",
        "    move-result v3",
        "    if-lez v3, :ahnali_http_async_json_error_empty",
        "    :ahnali_http_async_json_error_try_start",
        "    new-instance v4, Lorg/json/JSONObject;",
        "    invoke-direct {v4, v2}, Lorg/json/JSONObject;-><init>(Ljava/lang/String;)V",
        "    invoke-virtual {v4, p1}, Lorg/json/JSONObject;->has(Ljava/lang/String;)Z",
        "    move-result v5",
        "    if-eqz v5, :ahnali_http_async_json_error_missing_key",
        "    invoke-virtual {v4, p1}, Lorg/json/JSONObject;->isNull(Ljava/lang/String;)Z",
        "    move-result v5",
        "    if-nez v5, :ahnali_http_async_json_error_missing_key",
        "    const/4 v0, 0x0",
        "    return v0",
        "    :ahnali_http_async_json_error_try_end",
        "    .catch Lorg/json/JSONException; {:ahnali_http_async_json_error_try_start .. :ahnali_http_async_json_error_try_end} :ahnali_http_async_json_error_malformed",
        "    .catch Ljava/lang/Exception; {:ahnali_http_async_json_error_try_start .. :ahnali_http_async_json_error_try_end} :ahnali_http_async_json_error_exception",
        "    :ahnali_http_async_json_error_missing_key",
        "    const/4 v0, 0x6",
        "    return v0",
        "    :ahnali_http_async_json_error_empty",
        "    const/4 v0, 0x4",
        "    return v0",
        "    :ahnali_http_async_json_error_invalid",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_http_async_json_error_malformed",
        "    const/4 v0, 0x5",
        "    return v0",
        "    :ahnali_http_async_json_error_exception",
        "    const/4 v0, 0x2",
        "    return v0",
        ".end method",
    ]


def _emit_http_get_async_json_field_method() -> list[str]:
    return [
        ".method public static getAsyncJsonField(ILjava/lang/String;Ljava/lang/String;)Ljava/lang/String;",
        "    .locals 6",
        "    invoke-static {p0, p1}, Lcom/ahnali/runtime/HttpHelper;->getAsyncJsonFieldError(ILjava/lang/String;)I",
        "    move-result v0",
        "    if-nez v0, :ahnali_http_async_json_field_fallback",
        '    const-string v1, ""',
        "    invoke-static {p0, v1}, Lcom/ahnali/runtime/HttpHelper;->getAsyncBody(ILjava/lang/String;)Ljava/lang/String;",
        "    move-result-object v2",
        "    if-eqz v2, :ahnali_http_async_json_field_fallback",
        "    :ahnali_http_async_json_field_try_start",
        "    new-instance v3, Lorg/json/JSONObject;",
        "    invoke-direct {v3, v2}, Lorg/json/JSONObject;-><init>(Ljava/lang/String;)V",
        "    invoke-virtual {v3, p1}, Lorg/json/JSONObject;->opt(Ljava/lang/String;)Ljava/lang/Object;",
        "    move-result-object v4",
        "    if-eqz v4, :ahnali_http_async_json_field_fallback",
        "    invoke-virtual {v4}, Ljava/lang/Object;->toString()Ljava/lang/String;",
        "    move-result-object v5",
        "    if-eqz v5, :ahnali_http_async_json_field_fallback",
        "    return-object v5",
        "    :ahnali_http_async_json_field_try_end",
        "    .catch Lorg/json/JSONException; {:ahnali_http_async_json_field_try_start .. :ahnali_http_async_json_field_try_end} :ahnali_http_async_json_field_fallback",
        "    .catch Ljava/lang/Exception; {:ahnali_http_async_json_field_try_start .. :ahnali_http_async_json_field_try_end} :ahnali_http_async_json_field_fallback",
        "    :ahnali_http_async_json_field_fallback",
        "    return-object p2",
        ".end method",
    ]


def _emit_http_get_async_json_array_length_error_method() -> list[str]:
    return [
        ".method public static getAsyncJsonArrayLengthError(I)I",
        "    .locals 5",
        "    invoke-static {p0}, Lcom/ahnali/runtime/HttpHelper;->getAsyncError(I)I",
        "    move-result v0",
        "    if-eqz v0, :ahnali_http_async_json_arr_error_body",
        "    return v0",
        "    :ahnali_http_async_json_arr_error_body",
        '    const-string v1, ""',
        "    invoke-static {p0, v1}, Lcom/ahnali/runtime/HttpHelper;->getAsyncBody(ILjava/lang/String;)Ljava/lang/String;",
        "    move-result-object v2",
        "    if-eqz v2, :ahnali_http_async_json_arr_error_empty",
        "    invoke-virtual {v2}, Ljava/lang/String;->length()I",
        "    move-result v3",
        "    if-lez v3, :ahnali_http_async_json_arr_error_empty",
        "    :ahnali_http_async_json_arr_error_try_start",
        "    new-instance v4, Lorg/json/JSONArray;",
        "    invoke-direct {v4, v2}, Lorg/json/JSONArray;-><init>(Ljava/lang/String;)V",
        "    const/4 v0, 0x0",
        "    return v0",
        "    :ahnali_http_async_json_arr_error_try_end",
        "    .catch Lorg/json/JSONException; {:ahnali_http_async_json_arr_error_try_start .. :ahnali_http_async_json_arr_error_try_end} :ahnali_http_async_json_arr_error_malformed",
        "    .catch Ljava/lang/Exception; {:ahnali_http_async_json_arr_error_try_start .. :ahnali_http_async_json_arr_error_try_end} :ahnali_http_async_json_arr_error_exception",
        "    :ahnali_http_async_json_arr_error_empty",
        "    const/4 v0, 0x4",
        "    return v0",
        "    :ahnali_http_async_json_arr_error_malformed",
        "    const/4 v0, 0x5",
        "    return v0",
        "    :ahnali_http_async_json_arr_error_exception",
        "    const/4 v0, 0x2",
        "    return v0",
        ".end method",
    ]


def _emit_http_get_async_json_array_length_method() -> list[str]:
    return [
        ".method public static getAsyncJsonArrayLength(II)I",
        "    .locals 4",
        "    invoke-static {p0}, Lcom/ahnali/runtime/HttpHelper;->getAsyncJsonArrayLengthError(I)I",
        "    move-result v0",
        "    if-nez v0, :ahnali_http_async_json_arr_fallback",
        '    const-string v1, "[]"',
        "    invoke-static {p0, v1}, Lcom/ahnali/runtime/HttpHelper;->getAsyncBody(ILjava/lang/String;)Ljava/lang/String;",
        "    move-result-object v2",
        "    :ahnali_http_async_json_arr_try_start",
        "    new-instance v3, Lorg/json/JSONArray;",
        "    invoke-direct {v3, v2}, Lorg/json/JSONArray;-><init>(Ljava/lang/String;)V",
        "    invoke-virtual {v3}, Lorg/json/JSONArray;->length()I",
        "    move-result v0",
        "    return v0",
        "    :ahnali_http_async_json_arr_try_end",
        "    .catch Lorg/json/JSONException; {:ahnali_http_async_json_arr_try_start .. :ahnali_http_async_json_arr_try_end} :ahnali_http_async_json_arr_fallback",
        "    .catch Ljava/lang/Exception; {:ahnali_http_async_json_arr_try_start .. :ahnali_http_async_json_arr_try_end} :ahnali_http_async_json_arr_fallback",
        "    :ahnali_http_async_json_arr_fallback",
        "    return p1",
        ".end method",
    ]


def _sanitize_method_tag(method_name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(method_name).strip().lower())


def _emit_pref_put_string_method(method_name: str, pref_name: str) -> list[str]:
    tag = _sanitize_method_tag(method_name)
    fail = f":ahnali_{tag}_fail"
    try_start = f":ahnali_{tag}_try_start"
    try_end = f":ahnali_{tag}_try_end"
    return [
        f".method public static {method_name}(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I",
        "    .locals 4",
        f"    if-eqz p0, {fail}",
        f"    if-eqz p1, {fail}",
        f"    {try_start}",
        f'    const-string v0, "{pref_name}"',
        "    const/4 v1, 0x0",
        "    invoke-virtual {p0, v0, v1}, Landroid/app/Activity;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;",
        "    move-result-object v2",
        f"    if-eqz v2, {fail}",
        "    invoke-interface {v2}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;",
        "    move-result-object v3",
        "    invoke-interface {v3, p1, p2}, Landroid/content/SharedPreferences$Editor;->putString(Ljava/lang/String;Ljava/lang/String;)Landroid/content/SharedPreferences$Editor;",
        "    move-result-object v3",
        "    invoke-interface {v3}, Landroid/content/SharedPreferences$Editor;->apply()V",
        "    const/4 v0, 0x1",
        "    return v0",
        f"    {try_end}",
        f"    .catch Ljava/lang/Exception; {{{try_start} .. {try_end}}} {fail}",
        f"    {fail}",
        "    const/4 v0, 0x0",
        "    return v0",
        ".end method",
    ]


def _emit_pref_get_string_method(method_name: str, pref_name: str) -> list[str]:
    tag = _sanitize_method_tag(method_name)
    fallback = f":ahnali_{tag}_fallback"
    try_start = f":ahnali_{tag}_try_start"
    try_end = f":ahnali_{tag}_try_end"
    return [
        f".method public static {method_name}(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;",
        "    .locals 4",
        f"    if-eqz p0, {fallback}",
        f"    if-eqz p1, {fallback}",
        f"    {try_start}",
        f'    const-string v0, "{pref_name}"',
        "    const/4 v1, 0x0",
        "    invoke-virtual {p0, v0, v1}, Landroid/app/Activity;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;",
        "    move-result-object v2",
        f"    if-eqz v2, {fallback}",
        "    invoke-interface {v2, p1, p2}, Landroid/content/SharedPreferences;->getString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;",
        "    move-result-object v3",
        f"    if-eqz v3, {fallback}",
        "    return-object v3",
        f"    {try_end}",
        f"    .catch Ljava/lang/Exception; {{{try_start} .. {try_end}}} {fallback}",
        f"    {fallback}",
        "    return-object p2",
        ".end method",
    ]


def _emit_pref_remove_method(method_name: str, pref_name: str) -> list[str]:
    tag = _sanitize_method_tag(method_name)
    fail = f":ahnali_{tag}_fail"
    try_start = f":ahnali_{tag}_try_start"
    try_end = f":ahnali_{tag}_try_end"
    return [
        f".method public static {method_name}(Landroid/app/Activity;Ljava/lang/String;)I",
        "    .locals 4",
        f"    if-eqz p0, {fail}",
        f"    if-eqz p1, {fail}",
        f"    {try_start}",
        f'    const-string v0, "{pref_name}"',
        "    const/4 v1, 0x0",
        "    invoke-virtual {p0, v0, v1}, Landroid/app/Activity;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;",
        "    move-result-object v2",
        f"    if-eqz v2, {fail}",
        "    invoke-interface {v2}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;",
        "    move-result-object v3",
        "    invoke-interface {v3, p1}, Landroid/content/SharedPreferences$Editor;->remove(Ljava/lang/String;)Landroid/content/SharedPreferences$Editor;",
        "    move-result-object v3",
        "    invoke-interface {v3}, Landroid/content/SharedPreferences$Editor;->apply()V",
        "    const/4 v0, 0x1",
        "    return v0",
        f"    {try_end}",
        f"    .catch Ljava/lang/Exception; {{{try_start} .. {try_end}}} {fail}",
        f"    {fail}",
        "    const/4 v0, 0x0",
        "    return v0",
        ".end method",
    ]


def _emit_pref_exists_method(method_name: str, pref_name: str) -> list[str]:
    tag = _sanitize_method_tag(method_name)
    fail = f":ahnali_{tag}_fail"
    try_start = f":ahnali_{tag}_try_start"
    try_end = f":ahnali_{tag}_try_end"
    return [
        f".method public static {method_name}(Landroid/app/Activity;Ljava/lang/String;)I",
        "    .locals 4",
        f"    if-eqz p0, {fail}",
        f"    if-eqz p1, {fail}",
        f"    {try_start}",
        f'    const-string v0, "{pref_name}"',
        "    const/4 v1, 0x0",
        "    invoke-virtual {p0, v0, v1}, Landroid/app/Activity;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;",
        "    move-result-object v2",
        f"    if-eqz v2, {fail}",
        "    invoke-interface {v2, p1}, Landroid/content/SharedPreferences;->contains(Ljava/lang/String;)Z",
        "    move-result v3",
        "    return v3",
        f"    {try_end}",
        f"    .catch Ljava/lang/Exception; {{{try_start} .. {try_end}}} {fail}",
        f"    {fail}",
        "    const/4 v0, 0x0",
        "    return v0",
        ".end method",
    ]


def _emit_pref_clear_method(method_name: str, pref_name: str) -> list[str]:
    tag = _sanitize_method_tag(method_name)
    fail = f":ahnali_{tag}_fail"
    try_start = f":ahnali_{tag}_try_start"
    try_end = f":ahnali_{tag}_try_end"
    return [
        f".method public static {method_name}(Landroid/app/Activity;)I",
        "    .locals 4",
        f"    if-eqz p0, {fail}",
        f"    {try_start}",
        f'    const-string v0, "{pref_name}"',
        "    const/4 v1, 0x0",
        "    invoke-virtual {p0, v0, v1}, Landroid/app/Activity;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;",
        "    move-result-object v2",
        f"    if-eqz v2, {fail}",
        "    invoke-interface {v2}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;",
        "    move-result-object v3",
        "    invoke-interface {v3}, Landroid/content/SharedPreferences$Editor;->clear()Landroid/content/SharedPreferences$Editor;",
        "    move-result-object v3",
        "    invoke-interface {v3}, Landroid/content/SharedPreferences$Editor;->apply()V",
        "    const/4 v0, 0x1",
        "    return v0",
        f"    {try_end}",
        f"    .catch Ljava/lang/Exception; {{{try_start} .. {try_end}}} {fail}",
        f"    {fail}",
        "    const/4 v0, 0x0",
        "    return v0",
        ".end method",
    ]


def _emit_storage_put_string_method() -> list[str]:
    return _emit_pref_put_string_method("putString", "ahnali_storage")


def _emit_storage_get_string_method() -> list[str]:
    return _emit_pref_get_string_method("getString", "ahnali_storage")


def _emit_storage_remove_method() -> list[str]:
    return _emit_pref_remove_method("remove", "ahnali_storage")


def _emit_storage_exists_method() -> list[str]:
    return _emit_pref_exists_method("exists", "ahnali_storage")


def _emit_storage_clear_method() -> list[str]:
    return _emit_pref_clear_method("clear", "ahnali_storage")


def emit_capability_helper_smali(
    *,
    class_desc: str,
    helper_method: str,
    helper_sig: str,
) -> str:
    _args, ret_desc = _parse_method_sig(helper_sig)
    lines = [
        f".class public final {class_desc}",
        ".super Ljava/lang/Object;",
        "",
        ".method public constructor <init>()V",
        "    .locals 0",
        "    invoke-direct {p0}, Ljava/lang/Object;-><init>()V",
        "    return-void",
        ".end method",
        "",
    ]

    if (
        class_desc == "Lcom/ahnali/runtime/UrlLauncherHelper;"
        and helper_method == "openUrl"
        and helper_sig == "(Landroid/app/Activity;Ljava/lang/String;)I"
    ):
        lines.extend(_emit_url_launcher_open_url_method())
        return "\n".join(lines)

    if (
        class_desc == "Lcom/ahnali/runtime/ConnectivityHelper;"
        and helper_method == "isConnected"
        and helper_sig == "(Landroid/app/Activity;)I"
    ):
        lines.extend(_emit_connectivity_is_connected_method())
        return "\n".join(lines)

    if (
        class_desc == "Lcom/ahnali/runtime/LocationHelper;"
        and helper_method == "isLocationEnabled"
        and helper_sig == "(Landroid/app/Activity;)I"
    ):
        lines.extend(_emit_location_is_enabled_method())
        return "\n".join(lines)

    if (
        class_desc == "Lcom/ahnali/runtime/PermissionHelper;"
        and helper_method == "isGranted"
        and helper_sig == "(Landroid/app/Activity;Ljava/lang/String;)I"
    ):
        lines.extend(_emit_permission_is_granted_method())
        return "\n".join(lines)

    if (
        class_desc == "Lcom/ahnali/runtime/WebHelper;"
        and helper_method == "loadUrl"
        and helper_sig == "(Landroid/app/Activity;Ljava/lang/String;)I"
    ):
        lines.insert(3, ".field private static sJsEnabled:I")
        lines.insert(4, ".field private static sDomStorage:I")
        lines.insert(5, ".field private static sAllowFileAccess:I")
        lines.insert(6, ".field private static sAllowCleartext:I")
        lines.insert(7, "")
        lines.extend(_emit_web_set_policy_method())
        lines.append("")
        lines.extend(_emit_web_load_url_method())
        lines.append("")
        lines.extend(_emit_web_load_url_error_method())
        return "\n".join(lines)

    if (
        class_desc == "Lcom/ahnali/runtime/NotificationHelper;"
        and helper_method == "postNotification"
        and helper_sig == "(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I"
    ):
        lines.extend(_emit_notification_create_channel_method())
        lines.append("")
        lines.extend(_emit_notification_post_method())
        lines.append("")
        lines.extend(_emit_notification_post_error_method())
        return "\n".join(lines)

    if (
        class_desc == "Lcom/ahnali/runtime/ClipboardHelper;"
        and helper_method == "setText"
        and helper_sig == "(Landroid/app/Activity;Ljava/lang/String;)I"
    ):
        lines.extend(_emit_clipboard_set_text_method())
        lines.append("")
        lines.extend(_emit_clipboard_get_text_method())
        return "\n".join(lines)

    if (
        class_desc == "Lcom/ahnali/runtime/ShareHelper;"
        and helper_method == "shareText"
        and helper_sig == "(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I"
    ):
        lines.extend(_emit_share_text_method())
        lines.append("")
        lines.extend(_emit_share_text_error_method())
        lines.append("")
        lines.extend(_emit_open_uri_method())
        lines.append("")
        lines.extend(_emit_open_uri_error_method())
        return "\n".join(lines)

    if (
        class_desc == "Lcom/ahnali/runtime/HttpHelper;"
        and helper_method == "httpGet"
        and helper_sig == "(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;"
    ):
        lines.insert(3, ".field private static sAsyncNextToken:I")
        lines.insert(4, ".field private static sAsyncToken:I")
        lines.insert(5, ".field private static sAsyncCancelByToken:Landroid/util/SparseIntArray;")
        lines.insert(6, ".field private static sAsyncProgressByToken:Landroid/util/SparseIntArray;")
        lines.insert(7, ".field private static sAsyncErrorByToken:Landroid/util/SparseIntArray;")
        lines.insert(8, ".field private static sAsyncStatusByToken:Landroid/util/SparseIntArray;")
        lines.insert(9, ".field private static sAsyncBodyByToken:Ljava/util/HashMap;")
        lines.insert(10, "")
        lines.extend(_emit_http_get_method())
        lines.append("")
        lines.extend(_emit_http_get_status_method())
        lines.append("")
        lines.extend(_emit_http_get_error_method())
        lines.append("")
        lines.extend(_emit_http_get_with_timeout_method())
        lines.append("")
        lines.extend(_emit_http_get_status_with_timeout_method())
        lines.append("")
        lines.extend(_emit_http_get_error_with_timeout_method())
        lines.append("")
        lines.extend(_emit_http_resolve_request_method_method())
        lines.append("")
        lines.extend(_emit_http_apply_request_headers_method())
        lines.append("")
        lines.extend(_emit_http_apply_request_body_method())
        lines.append("")
        lines.extend(_emit_http_request_with_timeout_method())
        lines.append("")
        lines.extend(_emit_http_request_status_with_timeout_method())
        lines.append("")
        lines.extend(_emit_http_request_error_with_timeout_method())
        lines.append("")
        lines.extend(_emit_http_get_retry_method())
        lines.append("")
        lines.extend(_emit_http_get_json_field_error_method())
        lines.append("")
        lines.extend(_emit_http_get_json_field_method())
        lines.append("")
        lines.extend(_emit_http_ensure_async_store_method())
        lines.append("")
        lines.extend(_emit_http_init_async_token_method())
        lines.append("")
        lines.extend(_emit_http_get_current_async_token_method())
        lines.append("")
        lines.extend(_emit_http_next_async_token_method())
        lines.append("")
        lines.extend(_emit_http_start_async_method())
        lines.append("")
        lines.extend(_emit_http_start_async_with_token_method())
        lines.append("")
        lines.extend(_emit_http_cancel_async_method())
        lines.append("")
        lines.extend(_emit_http_should_cancel_method())
        lines.append("")
        lines.extend(_emit_http_set_async_progress_method())
        lines.append("")
        lines.extend(_emit_http_get_async_progress_method())
        lines.append("")
        lines.extend(_emit_http_set_async_error_method())
        lines.append("")
        lines.extend(_emit_http_get_async_error_method())
        lines.append("")
        lines.extend(_emit_http_set_async_status_method())
        lines.append("")
        lines.extend(_emit_http_get_async_status_method())
        lines.append("")
        lines.extend(_emit_http_set_async_body_method())
        lines.append("")
        lines.extend(_emit_http_get_async_body_method())
        lines.append("")
        lines.extend(_emit_http_get_async_json_field_error_method())
        lines.append("")
        lines.extend(_emit_http_get_async_json_field_method())
        lines.append("")
        lines.extend(_emit_http_get_async_json_array_length_error_method())
        lines.append("")
        lines.extend(_emit_http_get_async_json_array_length_method())
        return "\n".join(lines)

    if (
        class_desc == "Lcom/ahnali/runtime/StorageHelper;"
        and helper_method == "putString"
        and helper_sig == "(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I"
    ):
        families = [
            ("ahnali_storage", "putString", "getString", "remove", "exists", "clear"),
            (
                "ahnali_datastore",
                "dataStorePutString",
                "dataStoreGetString",
                "dataStoreRemove",
                "dataStoreExists",
                "dataStoreClear",
            ),
            ("ahnali_file", "fileWriteString", "fileReadString", "fileRemove", "fileExists", "fileClear"),
            ("ahnali_sqlite", "sqlitePutString", "sqliteGetString", "sqliteRemove", "sqliteExists", "sqliteClear"),
            ("ahnali_room", "roomPutString", "roomGetString", "roomRemove", "roomExists", "roomClear"),
            (
                "ahnali_encrypted",
                "encryptedPutString",
                "encryptedGetString",
                "encryptedRemove",
                "encryptedExists",
                "encryptedClear",
            ),
        ]
        for idx, (pref, put_name, get_name, remove_name, exists_name, clear_name) in enumerate(families):
            if idx > 0:
                lines.append("")
            lines.extend(_emit_pref_put_string_method(put_name, pref))
            lines.append("")
            lines.extend(_emit_pref_get_string_method(get_name, pref))
            lines.append("")
            lines.extend(_emit_pref_remove_method(remove_name, pref))
            lines.append("")
            lines.extend(_emit_pref_exists_method(exists_name, pref))
            lines.append("")
            lines.extend(_emit_pref_clear_method(clear_name, pref))
        return "\n".join(lines)

    locals_count = 0 if ret_desc == "V" else 2 if ret_desc in {"J", "D"} else 1
    lines.append(f".method public static {helper_method}{helper_sig}")
    lines.append(f"    .locals {locals_count}")
    lines.extend(_emit_default_method_body(ret_desc))
    lines.append(".end method")
    return "\n".join(lines)

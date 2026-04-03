from __future__ import annotations

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


def _emit_web_add_js_bridge_method() -> list[str]:
    return [
        ".method public static addJsBridge(Landroid/app/Activity;Ljava/lang/String;)I",
        "    .locals 2",
        "    invoke-static {p0, p1}, Lcom/ahnali/runtime/WebHelper;->addJsBridgeError(Landroid/app/Activity;Ljava/lang/String;)I",
        "    move-result v0",
        "    if-nez v0, :ahnali_web_bridge_fail",
        "    const/4 v1, 0x1",
        "    return v1",
        "    :ahnali_web_bridge_fail",
        "    const/4 v1, 0x0",
        "    return v1",
        ".end method",
    ]


def _emit_web_add_js_bridge_error_method() -> list[str]:
    return [
        ".method public static addJsBridgeError(Landroid/app/Activity;Ljava/lang/String;)I",
        "    .locals 8",
        "    if-eqz p0, :ahnali_web_bridge_invalid",
        "    if-eqz p1, :ahnali_web_bridge_invalid",
        "    invoke-virtual {p1}, Ljava/lang/String;->length()I",
        "    move-result v0",
        "    if-lez v0, :ahnali_web_bridge_invalid",
        "    sget v1, Lcom/ahnali/runtime/WebHelper;->sJsEnabled:I",
        "    if-nez v1, :ahnali_web_bridge_js_ok",
        "    const/4 v0, 0x2",
        "    return v0",
        "    :ahnali_web_bridge_js_ok",
        '    const-string v2, "ahnali_"',
        "    invoke-virtual {p1, v2}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z",
        "    move-result v3",
        "    if-nez v3, :ahnali_web_bridge_name_ok",
        "    const/4 v0, 0x5",
        "    return v0",
        "    :ahnali_web_bridge_name_ok",
        "    :ahnali_web_bridge_try_start",
        "    new-instance v4, Landroid/webkit/WebView;",
        "    invoke-direct {v4, p0}, Landroid/webkit/WebView;-><init>(Landroid/content/Context;)V",
        "    invoke-virtual {v4}, Landroid/webkit/WebView;->getSettings()Landroid/webkit/WebSettings;",
        "    move-result-object v5",
        "    if-eqz v5, :ahnali_web_bridge_runtime_error",
        "    sget v6, Lcom/ahnali/runtime/WebHelper;->sJsEnabled:I",
        "    invoke-virtual {v5, v6}, Landroid/webkit/WebSettings;->setJavaScriptEnabled(Z)V",
        "    sget v7, Lcom/ahnali/runtime/WebHelper;->sDomStorage:I",
        "    invoke-virtual {v5, v7}, Landroid/webkit/WebSettings;->setDomStorageEnabled(Z)V",
        "    sget v6, Lcom/ahnali/runtime/WebHelper;->sAllowFileAccess:I",
        "    invoke-virtual {v5, v6}, Landroid/webkit/WebSettings;->setAllowFileAccess(Z)V",
        "    new-instance v7, Ljava/lang/Object;",
        "    invoke-direct {v7}, Ljava/lang/Object;-><init>()V",
        "    invoke-virtual {v4, v7, p1}, Landroid/webkit/WebView;->addJavascriptInterface(Ljava/lang/Object;Ljava/lang/String;)V",
        "    const/4 v0, 0x0",
        "    return v0",
        "    :ahnali_web_bridge_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_web_bridge_try_start .. :ahnali_web_bridge_try_end} :ahnali_web_bridge_exception",
        "    :ahnali_web_bridge_invalid",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_web_bridge_runtime_error",
        "    const/4 v0, 0x3",
        "    return v0",
        "    :ahnali_web_bridge_exception",
        "    const/4 v0, 0x4",
        "    return v0",
        ".end method",
    ]


def _emit_web_choose_file_method() -> list[str]:
    return [
        ".method public static chooseFile(Landroid/app/Activity;Ljava/lang/String;)I",
        "    .locals 2",
        "    invoke-static {p0, p1}, Lcom/ahnali/runtime/WebHelper;->chooseFileError(Landroid/app/Activity;Ljava/lang/String;)I",
        "    move-result v0",
        "    if-nez v0, :ahnali_web_choose_file_fail",
        "    const/4 v1, 0x1",
        "    return v1",
        "    :ahnali_web_choose_file_fail",
        "    const/4 v1, 0x0",
        "    return v1",
        ".end method",
    ]


def _emit_web_choose_file_error_method() -> list[str]:
    return [
        ".method public static chooseFileError(Landroid/app/Activity;Ljava/lang/String;)I",
        "    .locals 7",
        "    if-eqz p0, :ahnali_web_choose_file_invalid",
        "    if-eqz p1, :ahnali_web_choose_file_invalid",
        "    :ahnali_web_choose_file_try_start",
        "    new-instance v1, Landroid/content/Intent;",
        '    const-string v2, "android.intent.action.GET_CONTENT"',
        "    invoke-direct {v1, v2}, Landroid/content/Intent;-><init>(Ljava/lang/String;)V",
        "    invoke-virtual {v1, p1}, Landroid/content/Intent;->setType(Ljava/lang/String;)Landroid/content/Intent;",
        '    const-string v3, "android.intent.category.OPENABLE"',
        "    invoke-virtual {v1, v3}, Landroid/content/Intent;->addCategory(Ljava/lang/String;)Landroid/content/Intent;",
        "    move-result-object v1",
        '    const-string v4, "Select file"',
        "    invoke-static {v1, v4}, Landroid/content/Intent;->createChooser(Landroid/content/Intent;Ljava/lang/CharSequence;)Landroid/content/Intent;",
        "    move-result-object v5",
        "    invoke-virtual {p0, v5}, Landroid/app/Activity;->startActivity(Landroid/content/Intent;)V",
        "    const/4 v0, 0x0",
        "    return v0",
        "    :ahnali_web_choose_file_try_end",
        "    .catch Landroid/content/ActivityNotFoundException; {:ahnali_web_choose_file_try_start .. :ahnali_web_choose_file_try_end} :ahnali_web_choose_file_not_found",
        "    .catch Ljava/lang/Exception; {:ahnali_web_choose_file_try_start .. :ahnali_web_choose_file_try_end} :ahnali_web_choose_file_exception",
        "    :ahnali_web_choose_file_invalid",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_web_choose_file_not_found",
        "    const/4 v0, 0x3",
        "    return v0",
        "    :ahnali_web_choose_file_exception",
        "    const/4 v0, 0x4",
        "    return v0",
        ".end method",
    ]


def _emit_web_set_cookie_method() -> list[str]:
    return [
        ".method public static setCookie(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I",
        "    .locals 2",
        "    invoke-static {p0, p1, p2}, Lcom/ahnali/runtime/WebHelper;->setCookieError(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I",
        "    move-result v0",
        "    if-nez v0, :ahnali_web_set_cookie_fail",
        "    const/4 v1, 0x1",
        "    return v1",
        "    :ahnali_web_set_cookie_fail",
        "    const/4 v1, 0x0",
        "    return v1",
        ".end method",
    ]


def _emit_web_set_cookie_error_method() -> list[str]:
    return [
        ".method public static setCookieError(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I",
        "    .locals 4",
        "    if-eqz p0, :ahnali_web_set_cookie_invalid",
        "    if-eqz p1, :ahnali_web_set_cookie_invalid",
        "    if-eqz p2, :ahnali_web_set_cookie_invalid",
        "    :ahnali_web_set_cookie_try_start",
        "    invoke-static {}, Landroid/webkit/CookieManager;->getInstance()Landroid/webkit/CookieManager;",
        "    move-result-object v1",
        "    if-eqz v1, :ahnali_web_set_cookie_missing",
        "    invoke-virtual {v1, p1, p2}, Landroid/webkit/CookieManager;->setCookie(Ljava/lang/String;Ljava/lang/String;)V",
        "    const/4 v0, 0x0",
        "    return v0",
        "    :ahnali_web_set_cookie_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_web_set_cookie_try_start .. :ahnali_web_set_cookie_try_end} :ahnali_web_set_cookie_exception",
        "    :ahnali_web_set_cookie_invalid",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_web_set_cookie_missing",
        "    const/4 v0, 0x3",
        "    return v0",
        "    :ahnali_web_set_cookie_exception",
        "    const/4 v0, 0x4",
        "    return v0",
        ".end method",
    ]


def _emit_web_get_cookie_method() -> list[str]:
    return [
        ".method public static getCookie(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;",
        "    .locals 4",
        "    if-eqz p0, :ahnali_web_get_cookie_fallback",
        "    if-eqz p1, :ahnali_web_get_cookie_fallback",
        "    :ahnali_web_get_cookie_try_start",
        "    invoke-static {}, Landroid/webkit/CookieManager;->getInstance()Landroid/webkit/CookieManager;",
        "    move-result-object v1",
        "    if-eqz v1, :ahnali_web_get_cookie_fallback",
        "    invoke-virtual {v1, p1}, Landroid/webkit/CookieManager;->getCookie(Ljava/lang/String;)Ljava/lang/String;",
        "    move-result-object v2",
        "    if-eqz v2, :ahnali_web_get_cookie_fallback",
        "    return-object v2",
        "    :ahnali_web_get_cookie_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_web_get_cookie_try_start .. :ahnali_web_get_cookie_try_end} :ahnali_web_get_cookie_fallback",
        "    :ahnali_web_get_cookie_fallback",
        "    return-object p2",
        ".end method",
    ]


def _emit_web_get_cookie_error_method() -> list[str]:
    return [
        ".method public static getCookieError(Landroid/app/Activity;Ljava/lang/String;)I",
        "    .locals 3",
        "    if-eqz p0, :ahnali_web_get_cookie_error_invalid",
        "    if-eqz p1, :ahnali_web_get_cookie_error_invalid",
        "    :ahnali_web_get_cookie_error_try_start",
        "    invoke-static {}, Landroid/webkit/CookieManager;->getInstance()Landroid/webkit/CookieManager;",
        "    move-result-object v1",
        "    if-eqz v1, :ahnali_web_get_cookie_error_missing",
        "    invoke-virtual {v1, p1}, Landroid/webkit/CookieManager;->getCookie(Ljava/lang/String;)Ljava/lang/String;",
        "    move-result-object v2",
        "    if-eqz v2, :ahnali_web_get_cookie_error_missing",
        "    const/4 v0, 0x0",
        "    return v0",
        "    :ahnali_web_get_cookie_error_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_web_get_cookie_error_try_start .. :ahnali_web_get_cookie_error_try_end} :ahnali_web_get_cookie_error_exception",
        "    :ahnali_web_get_cookie_error_invalid",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_web_get_cookie_error_missing",
        "    const/4 v0, 0x3",
        "    return v0",
        "    :ahnali_web_get_cookie_error_exception",
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


def _emit_share_file_method() -> list[str]:
    return [
        ".method public static shareFile(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I",
        "    .locals 2",
        "    invoke-static {p0, p1, p2, p3}, Lcom/ahnali/runtime/ShareHelper;->shareFileError(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I",
        "    move-result v0",
        "    if-nez v0, :ahnali_share_file_fail",
        "    const/4 v1, 0x1",
        "    return v1",
        "    :ahnali_share_file_fail",
        "    const/4 v1, 0x0",
        "    return v1",
        ".end method",
    ]


def _emit_share_file_error_method() -> list[str]:
    return [
        ".method public static shareFileError(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I",
        "    .locals 8",
        "    if-eqz p0, :ahnali_share_file_invalid",
        "    if-eqz p1, :ahnali_share_file_invalid",
        "    if-eqz p2, :ahnali_share_file_invalid",
        "    if-eqz p3, :ahnali_share_file_invalid",
        "    :ahnali_share_file_try_start",
        "    new-instance v1, Landroid/content/Intent;",
        '    const-string v2, "android.intent.action.SEND"',
        "    invoke-direct {v1, v2}, Landroid/content/Intent;-><init>(Ljava/lang/String;)V",
        "    invoke-virtual {v1, p3}, Landroid/content/Intent;->setType(Ljava/lang/String;)Landroid/content/Intent;",
        '    const-string v4, "android.intent.extra.STREAM"',
        "    invoke-static {p1}, Landroid/net/Uri;->parse(Ljava/lang/String;)Landroid/net/Uri;",
        "    move-result-object v5",
        "    invoke-virtual {v1, v4, v5}, Landroid/content/Intent;->putExtra(Ljava/lang/String;Landroid/os/Parcelable;)Landroid/content/Intent;",
        "    invoke-static {v1, p2}, Landroid/content/Intent;->createChooser(Landroid/content/Intent;Ljava/lang/CharSequence;)Landroid/content/Intent;",
        "    move-result-object v6",
        "    invoke-virtual {p0, v6}, Landroid/app/Activity;->startActivity(Landroid/content/Intent;)V",
        "    const/4 v0, 0x0",
        "    return v0",
        "    :ahnali_share_file_try_end",
        "    .catch Landroid/content/ActivityNotFoundException; {:ahnali_share_file_try_start .. :ahnali_share_file_try_end} :ahnali_share_file_not_found",
        "    .catch Ljava/lang/Exception; {:ahnali_share_file_try_start .. :ahnali_share_file_try_end} :ahnali_share_file_exception",
        "    :ahnali_share_file_invalid",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_share_file_not_found",
        "    const/4 v0, 0x3",
        "    return v0",
        "    :ahnali_share_file_exception",
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


def append_service_helpers(*, lines: list[str], class_desc: str, helper_method: str, helper_sig: str) -> bool:
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
        lines.extend(_emit_web_add_js_bridge_method())
        lines.append("")
        lines.extend(_emit_web_add_js_bridge_error_method())
        lines.append("")
        lines.extend(_emit_web_choose_file_method())
        lines.append("")
        lines.extend(_emit_web_choose_file_error_method())
        lines.append("")
        lines.extend(_emit_web_set_cookie_method())
        lines.append("")
        lines.extend(_emit_web_set_cookie_error_method())
        lines.append("")
        lines.extend(_emit_web_get_cookie_method())
        lines.append("")
        lines.extend(_emit_web_get_cookie_error_method())
        lines.append("")
        lines.extend(_emit_web_load_url_method())
        lines.append("")
        lines.extend(_emit_web_load_url_error_method())
        return True

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
        return True

    if (
        class_desc == "Lcom/ahnali/runtime/ClipboardHelper;"
        and helper_method == "setText"
        and helper_sig == "(Landroid/app/Activity;Ljava/lang/String;)I"
    ):
        lines.extend(_emit_clipboard_set_text_method())
        lines.append("")
        lines.extend(_emit_clipboard_get_text_method())
        return True

    if (
        class_desc == "Lcom/ahnali/runtime/ShareHelper;"
        and helper_method == "shareText"
        and helper_sig == "(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I"
    ):
        lines.extend(_emit_share_text_method())
        lines.append("")
        lines.extend(_emit_share_text_error_method())
        lines.append("")
        lines.extend(_emit_share_file_method())
        lines.append("")
        lines.extend(_emit_share_file_error_method())
        lines.append("")
        lines.extend(_emit_open_uri_method())
        lines.append("")
        lines.extend(_emit_open_uri_error_method())
        return True

    return False

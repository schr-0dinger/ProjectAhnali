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


def _emit_http_get_method() -> list[str]:
    return [
        ".method public static httpGet(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;",
        "    .locals 8",
        "    if-eqz p1, :ahnali_http_get_fallback",
        "    :ahnali_http_get_try_start",
        "    new-instance v0, Ljava/net/URL;",
        "    invoke-direct {v0, p1}, Ljava/net/URL;-><init>(Ljava/lang/String;)V",
        "    invoke-virtual {v0}, Ljava/net/URL;->openConnection()Ljava/net/URLConnection;",
        "    move-result-object v1",
        "    check-cast v1, Ljava/net/HttpURLConnection;",
        "    if-eqz v1, :ahnali_http_get_fallback",
        '    const-string v2, "GET"',
        "    invoke-virtual {v1, v2}, Ljava/net/HttpURLConnection;->setRequestMethod(Ljava/lang/String;)V",
        "    const/16 v2, 0x1f40",
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


def _emit_http_get_status_method() -> list[str]:
    return [
        ".method public static httpGetStatus(Landroid/app/Activity;Ljava/lang/String;)I",
        "    .locals 5",
        "    if-eqz p1, :ahnali_http_status_fail",
        "    :ahnali_http_status_try_start",
        "    new-instance v0, Ljava/net/URL;",
        "    invoke-direct {v0, p1}, Ljava/net/URL;-><init>(Ljava/lang/String;)V",
        "    invoke-virtual {v0}, Ljava/net/URL;->openConnection()Ljava/net/URLConnection;",
        "    move-result-object v1",
        "    check-cast v1, Ljava/net/HttpURLConnection;",
        "    if-eqz v1, :ahnali_http_status_fail",
        '    const-string v2, "GET"',
        "    invoke-virtual {v1, v2}, Ljava/net/HttpURLConnection;->setRequestMethod(Ljava/lang/String;)V",
        "    const/16 v2, 0x1f40",
        "    invoke-virtual {v1, v2}, Ljava/net/HttpURLConnection;->setConnectTimeout(I)V",
        "    invoke-virtual {v1, v2}, Ljava/net/HttpURLConnection;->setReadTimeout(I)V",
        "    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->getResponseCode()I",
        "    move-result v3",
        "    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->disconnect()V",
        "    return v3",
        "    :ahnali_http_status_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_http_status_try_start .. :ahnali_http_status_try_end} :ahnali_http_status_fail",
        "    :ahnali_http_status_fail",
        "    const/4 v0, -0x1",
        "    return v0",
        ".end method",
    ]


def _emit_http_get_error_method() -> list[str]:
    return [
        ".method public static httpGetError(Landroid/app/Activity;Ljava/lang/String;)I",
        "    .locals 8",
        "    if-eqz p1, :ahnali_http_error_invalid",
        "    :ahnali_http_error_try_start",
        "    new-instance v0, Ljava/net/URL;",
        "    invoke-direct {v0, p1}, Ljava/net/URL;-><init>(Ljava/lang/String;)V",
        "    invoke-virtual {v0}, Ljava/net/URL;->openConnection()Ljava/net/URLConnection;",
        "    move-result-object v1",
        "    check-cast v1, Ljava/net/HttpURLConnection;",
        "    if-eqz v1, :ahnali_http_error_exception",
        '    const-string v2, "GET"',
        "    invoke-virtual {v1, v2}, Ljava/net/HttpURLConnection;->setRequestMethod(Ljava/lang/String;)V",
        "    const/16 v2, 0x1f40",
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


def _emit_http_start_async_method() -> list[str]:
    return [
        ".method public static startAsync(Ljava/lang/Runnable;)I",
        "    .locals 2",
        "    if-eqz p0, :ahnali_http_async_fail",
        "    :ahnali_http_async_try_start",
        "    new-instance v0, Ljava/lang/Thread;",
        "    invoke-direct {v0, p0}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;)V",
        "    invoke-virtual {v0}, Ljava/lang/Thread;->start()V",
        "    const/4 v1, 0x1",
        "    return v1",
        "    :ahnali_http_async_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_http_async_try_start .. :ahnali_http_async_try_end} :ahnali_http_async_fail",
        "    :ahnali_http_async_fail",
        "    const/4 v0, 0x0",
        "    return v0",
        ".end method",
    ]


def _emit_storage_put_string_method() -> list[str]:
    return [
        ".method public static putString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I",
        "    .locals 4",
        "    if-eqz p0, :ahnali_storage_fail",
        "    if-eqz p1, :ahnali_storage_fail",
        "    :ahnali_storage_try_start",
        '    const-string v0, "ahnali_storage"',
        "    const/4 v1, 0x0",
        "    invoke-virtual {p0, v0, v1}, Landroid/app/Activity;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;",
        "    move-result-object v2",
        "    if-eqz v2, :ahnali_storage_fail",
        "    invoke-interface {v2}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;",
        "    move-result-object v3",
        "    invoke-interface {v3, p1, p2}, Landroid/content/SharedPreferences$Editor;->putString(Ljava/lang/String;Ljava/lang/String;)Landroid/content/SharedPreferences$Editor;",
        "    move-result-object v3",
        "    invoke-interface {v3}, Landroid/content/SharedPreferences$Editor;->apply()V",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_storage_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_storage_try_start .. :ahnali_storage_try_end} :ahnali_storage_fail",
        "    :ahnali_storage_fail",
        "    const/4 v0, 0x0",
        "    return v0",
        ".end method",
    ]


def _emit_storage_get_string_method() -> list[str]:
    return [
        ".method public static getString(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;",
        "    .locals 4",
        "    if-eqz p0, :ahnali_storage_get_fallback",
        "    if-eqz p1, :ahnali_storage_get_fallback",
        "    :ahnali_storage_get_try_start",
        '    const-string v0, "ahnali_storage"',
        "    const/4 v1, 0x0",
        "    invoke-virtual {p0, v0, v1}, Landroid/app/Activity;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;",
        "    move-result-object v2",
        "    if-eqz v2, :ahnali_storage_get_fallback",
        "    invoke-interface {v2, p1, p2}, Landroid/content/SharedPreferences;->getString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;",
        "    move-result-object v3",
        "    if-eqz v3, :ahnali_storage_get_fallback",
        "    return-object v3",
        "    :ahnali_storage_get_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_storage_get_try_start .. :ahnali_storage_get_try_end} :ahnali_storage_get_fallback",
        "    :ahnali_storage_get_fallback",
        "    return-object p2",
        ".end method",
    ]


def _emit_storage_remove_method() -> list[str]:
    return [
        ".method public static remove(Landroid/app/Activity;Ljava/lang/String;)I",
        "    .locals 4",
        "    if-eqz p0, :ahnali_storage_remove_fail",
        "    if-eqz p1, :ahnali_storage_remove_fail",
        "    :ahnali_storage_remove_try_start",
        '    const-string v0, "ahnali_storage"',
        "    const/4 v1, 0x0",
        "    invoke-virtual {p0, v0, v1}, Landroid/app/Activity;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;",
        "    move-result-object v2",
        "    if-eqz v2, :ahnali_storage_remove_fail",
        "    invoke-interface {v2}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;",
        "    move-result-object v3",
        "    invoke-interface {v3, p1}, Landroid/content/SharedPreferences$Editor;->remove(Ljava/lang/String;)Landroid/content/SharedPreferences$Editor;",
        "    move-result-object v3",
        "    invoke-interface {v3}, Landroid/content/SharedPreferences$Editor;->apply()V",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_storage_remove_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_storage_remove_try_start .. :ahnali_storage_remove_try_end} :ahnali_storage_remove_fail",
        "    :ahnali_storage_remove_fail",
        "    const/4 v0, 0x0",
        "    return v0",
        ".end method",
    ]


def _emit_storage_exists_method() -> list[str]:
    return [
        ".method public static exists(Landroid/app/Activity;Ljava/lang/String;)I",
        "    .locals 4",
        "    if-eqz p0, :ahnali_storage_exists_fail",
        "    if-eqz p1, :ahnali_storage_exists_fail",
        "    :ahnali_storage_exists_try_start",
        '    const-string v0, "ahnali_storage"',
        "    const/4 v1, 0x0",
        "    invoke-virtual {p0, v0, v1}, Landroid/app/Activity;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;",
        "    move-result-object v2",
        "    if-eqz v2, :ahnali_storage_exists_fail",
        "    invoke-interface {v2, p1}, Landroid/content/SharedPreferences;->contains(Ljava/lang/String;)Z",
        "    move-result v3",
        "    return v3",
        "    :ahnali_storage_exists_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_storage_exists_try_start .. :ahnali_storage_exists_try_end} :ahnali_storage_exists_fail",
        "    :ahnali_storage_exists_fail",
        "    const/4 v0, 0x0",
        "    return v0",
        ".end method",
    ]


def _emit_storage_clear_method() -> list[str]:
    return [
        ".method public static clear(Landroid/app/Activity;)I",
        "    .locals 4",
        "    if-eqz p0, :ahnali_storage_clear_fail",
        "    :ahnali_storage_clear_try_start",
        '    const-string v0, "ahnali_storage"',
        "    const/4 v1, 0x0",
        "    invoke-virtual {p0, v0, v1}, Landroid/app/Activity;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;",
        "    move-result-object v2",
        "    if-eqz v2, :ahnali_storage_clear_fail",
        "    invoke-interface {v2}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;",
        "    move-result-object v3",
        "    invoke-interface {v3}, Landroid/content/SharedPreferences$Editor;->clear()Landroid/content/SharedPreferences$Editor;",
        "    move-result-object v3",
        "    invoke-interface {v3}, Landroid/content/SharedPreferences$Editor;->apply()V",
        "    const/4 v0, 0x1",
        "    return v0",
        "    :ahnali_storage_clear_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_storage_clear_try_start .. :ahnali_storage_clear_try_end} :ahnali_storage_clear_fail",
        "    :ahnali_storage_clear_fail",
        "    const/4 v0, 0x0",
        "    return v0",
        ".end method",
    ]


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
        class_desc == "Lcom/ahnali/runtime/HttpHelper;"
        and helper_method == "httpGet"
        and helper_sig == "(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;"
    ):
        lines.extend(_emit_http_get_method())
        lines.append("")
        lines.extend(_emit_http_get_status_method())
        lines.append("")
        lines.extend(_emit_http_get_error_method())
        lines.append("")
        lines.extend(_emit_http_get_retry_method())
        lines.append("")
        lines.extend(_emit_http_get_json_field_error_method())
        lines.append("")
        lines.extend(_emit_http_get_json_field_method())
        lines.append("")
        lines.extend(_emit_http_start_async_method())
        return "\n".join(lines)

    if (
        class_desc == "Lcom/ahnali/runtime/StorageHelper;"
        and helper_method == "putString"
        and helper_sig == "(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I"
    ):
        lines.extend(_emit_storage_put_string_method())
        lines.append("")
        lines.extend(_emit_storage_get_string_method())
        lines.append("")
        lines.extend(_emit_storage_remove_method())
        lines.append("")
        lines.extend(_emit_storage_exists_method())
        lines.append("")
        lines.extend(_emit_storage_clear_method())
        return "\n".join(lines)

    locals_count = 0 if ret_desc == "V" else 2 if ret_desc in {"J", "D"} else 1
    lines.append(f".method public static {helper_method}{helper_sig}")
    lines.append(f"    .locals {locals_count}")
    lines.extend(_emit_default_method_body(ret_desc))
    lines.append(".end method")
    return "\n".join(lines)

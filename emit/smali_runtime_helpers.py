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
        class_desc == "Lcom/ahnali/runtime/StorageHelper;"
        and helper_method == "putString"
        and helper_sig == "(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)I"
    ):
        lines.extend(_emit_storage_put_string_method())
        lines.append("")
        lines.extend(_emit_storage_get_string_method())
        lines.append("")
        lines.extend(_emit_storage_remove_method())
        return "\n".join(lines)

    locals_count = 0 if ret_desc == "V" else 2 if ret_desc in {"J", "D"} else 1
    lines.append(f".method public static {helper_method}{helper_sig}")
    lines.append(f"    .locals {locals_count}")
    lines.extend(_emit_default_method_body(ret_desc))
    lines.append(".end method")
    return "\n".join(lines)

from __future__ import annotations

import re

from emit.capability_helpers import (
    append_networking_helpers,
    append_runtime_service_helpers,
    append_service_helpers,
    append_storage_helpers,
)



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


def _emit_reflection_get_text_method() -> list[str]:
    return [
        ".method public static getText(Landroid/widget/TextView;)Ljava/lang/String;",
        "    .locals 2",
        "    if-eqz p0, :ahnali_reflect_text_fail",
        "    :ahnali_reflect_text_try_start",
        "    invoke-virtual {p0}, Landroid/widget/TextView;->getText()Ljava/lang/CharSequence;",
        "    move-result-object v0",
        "    if-eqz v0, :ahnali_reflect_text_fail",
        "    invoke-interface {v0}, Ljava/lang/CharSequence;->toString()Ljava/lang/String;",
        "    move-result-object v1",
        "    return-object v1",
        "    :ahnali_reflect_text_try_end",
        "    .catch Ljava/lang/Exception; {:ahnali_reflect_text_try_start .. :ahnali_reflect_text_try_end} :ahnali_reflect_text_fail",
        "    :ahnali_reflect_text_fail",
        "    const/4 v0, 0x0",
        "    return-object v0",
        ".end method",
    ]


def _emit_list_wrapper_runtime_methods() -> list[str]:
    return [
        ".method public static create()Ljava/util/ArrayList;",
        "    .locals 1",
        "    new-instance v0, Ljava/util/ArrayList;",
        "    invoke-direct {v0}, Ljava/util/ArrayList;-><init>()V",
        "    return-object v0",
        ".end method",
        "",
        ".method public static addString(Ljava/util/ArrayList;Ljava/lang/String;)V",
        "    .locals 0",
        "    if-eqz p0, :ahnali_list_add_string_done",
        "    invoke-virtual {p0, p1}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z",
        "    :ahnali_list_add_string_done",
        "    return-void",
        ".end method",
        "",
        ".method public static addInt(Ljava/util/ArrayList;I)V",
        "    .locals 1",
        "    if-eqz p0, :ahnali_list_add_int_done",
        "    invoke-static {p1}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;",
        "    move-result-object v0",
        "    invoke-virtual {p0, v0}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z",
        "    :ahnali_list_add_int_done",
        "    return-void",
        ".end method",
        "",
        ".method public static size(Ljava/util/ArrayList;)I",
        "    .locals 1",
        "    if-eqz p0, :ahnali_list_size_fail",
        "    invoke-virtual {p0}, Ljava/util/ArrayList;->size()I",
        "    move-result v0",
        "    return v0",
        "    :ahnali_list_size_fail",
        "    const/4 v0, 0x0",
        "    return v0",
        ".end method",
    ]


def _emit_dict_wrapper_runtime_methods() -> list[str]:
    return [
        ".method public static create()Ljava/util/HashMap;",
        "    .locals 1",
        "    new-instance v0, Ljava/util/HashMap;",
        "    invoke-direct {v0}, Ljava/util/HashMap;-><init>()V",
        "    return-object v0",
        ".end method",
        "",
        ".method public static putString(Ljava/util/HashMap;Ljava/lang/String;Ljava/lang/String;)V",
        "    .locals 0",
        "    if-eqz p0, :ahnali_dict_put_string_done",
        "    invoke-virtual {p0, p1, p2}, Ljava/util/HashMap;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;",
        "    :ahnali_dict_put_string_done",
        "    return-void",
        ".end method",
        "",
        ".method public static putInt(Ljava/util/HashMap;Ljava/lang/String;I)V",
        "    .locals 1",
        "    if-eqz p0, :ahnali_dict_put_int_done",
        "    invoke-static {p2}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;",
        "    move-result-object v0",
        "    invoke-virtual {p0, p1, v0}, Ljava/util/HashMap;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;",
        "    :ahnali_dict_put_int_done",
        "    return-void",
        ".end method",
        "",
        ".method public static size(Ljava/util/HashMap;)I",
        "    .locals 1",
        "    if-eqz p0, :ahnali_dict_size_fail",
        "    invoke-virtual {p0}, Ljava/util/HashMap;->size()I",
        "    move-result v0",
        "    return v0",
        "    :ahnali_dict_size_fail",
        "    const/4 v0, 0x0",
        "    return v0",
        ".end method",
    ]


def _emit_set_wrapper_runtime_methods() -> list[str]:
    return [
        ".method public static create()Ljava/util/HashSet;",
        "    .locals 1",
        "    new-instance v0, Ljava/util/HashSet;",
        "    invoke-direct {v0}, Ljava/util/HashSet;-><init>()V",
        "    return-object v0",
        ".end method",
        "",
        ".method public static addString(Ljava/util/HashSet;Ljava/lang/String;)V",
        "    .locals 0",
        "    if-eqz p0, :ahnali_set_add_string_done",
        "    invoke-virtual {p0, p1}, Ljava/util/HashSet;->add(Ljava/lang/Object;)Z",
        "    :ahnali_set_add_string_done",
        "    return-void",
        ".end method",
        "",
        ".method public static addInt(Ljava/util/HashSet;I)V",
        "    .locals 1",
        "    if-eqz p0, :ahnali_set_add_int_done",
        "    invoke-static {p1}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;",
        "    move-result-object v0",
        "    invoke-virtual {p0, v0}, Ljava/util/HashSet;->add(Ljava/lang/Object;)Z",
        "    :ahnali_set_add_int_done",
        "    return-void",
        ".end method",
        "",
        ".method public static size(Ljava/util/HashSet;)I",
        "    .locals 1",
        "    if-eqz p0, :ahnali_set_size_fail",
        "    invoke-virtual {p0}, Ljava/util/HashSet;->size()I",
        "    move-result v0",
        "    return v0",
        "    :ahnali_set_size_fail",
        "    const/4 v0, 0x0",
        "    return v0",
        ".end method",
    ]


def _emit_tuple_wrapper_runtime_methods() -> list[str]:
    return [
        ".method public static create(I)[Ljava/lang/Object;",
        "    .locals 1",
        "    new-array v0, p0, [Ljava/lang/Object;",
        "    return-object v0",
        ".end method",
        "",
        ".method public static setString([Ljava/lang/Object;ILjava/lang/String;)V",
        "    .locals 0",
        "    if-eqz p0, :ahnali_tuple_set_string_done",
        "    aput-object p2, p0, p1",
        "    :ahnali_tuple_set_string_done",
        "    return-void",
        ".end method",
        "",
        ".method public static setInt([Ljava/lang/Object;II)V",
        "    .locals 1",
        "    if-eqz p0, :ahnali_tuple_set_int_done",
        "    invoke-static {p2}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;",
        "    move-result-object v0",
        "    aput-object v0, p0, p1",
        "    :ahnali_tuple_set_int_done",
        "    return-void",
        ".end method",
        "",
        ".method public static size([Ljava/lang/Object;)I",
        "    .locals 1",
        "    if-eqz p0, :ahnali_tuple_size_fail",
        "    array-length v0, p0",
        "    return v0",
        "    :ahnali_tuple_size_fail",
        "    const/4 v0, 0x0",
        "    return v0",
        ".end method",
    ]


def _emit_string_methods_runtime_methods() -> list[str]:
    return [
        ".method public static split(Ljava/lang/String;Ljava/lang/String;)Ljava/util/ArrayList;",
        "    .locals 6",
        "    new-instance v0, Ljava/util/ArrayList;",
        "    invoke-direct {v0}, Ljava/util/ArrayList;-><init>()V",
        "    if-eqz p0, :ahnali_string_split_done",
        "    if-eqz p1, :ahnali_string_split_done",
        "    invoke-virtual {p0, p1}, Ljava/lang/String;->split(Ljava/lang/String;)[Ljava/lang/String;",
        "    move-result-object v1",
        "    if-eqz v1, :ahnali_string_split_done",
        "    array-length v2, v1",
        "    const/4 v3, 0x0",
        "    :ahnali_string_split_loop",
        "    if-ge v3, v2, :ahnali_string_split_done",
        "    aget-object v4, v1, v3",
        "    invoke-virtual {v0, v4}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z",
        "    add-int/lit8 v3, v3, 0x1",
        "    goto :ahnali_string_split_loop",
        "    :ahnali_string_split_done",
        "    return-object v0",
        ".end method",
        "",
        ".method public static joinList(Ljava/lang/String;Ljava/util/ArrayList;)Ljava/lang/String;",
        "    .locals 7",
        "    new-instance v0, Ljava/lang/StringBuilder;",
        "    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V",
        "    if-nez p0, :ahnali_join_list_sep_ok",
        '    const-string p0, ""',
        "    :ahnali_join_list_sep_ok",
        "    if-eqz p1, :ahnali_join_list_done",
        "    invoke-virtual {p1}, Ljava/util/ArrayList;->size()I",
        "    move-result v1",
        "    const/4 v2, 0x0",
        "    :ahnali_join_list_loop",
        "    if-ge v2, v1, :ahnali_join_list_done",
        "    if-lez v2, :ahnali_join_list_skip_sep",
        "    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;",
        "    move-result-object v0",
        "    :ahnali_join_list_skip_sep",
        "    invoke-virtual {p1, v2}, Ljava/util/ArrayList;->get(I)Ljava/lang/Object;",
        "    move-result-object v3",
        "    invoke-static {v3}, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;",
        "    move-result-object v4",
        "    invoke-virtual {v0, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;",
        "    move-result-object v0",
        "    add-int/lit8 v2, v2, 0x1",
        "    goto :ahnali_join_list_loop",
        "    :ahnali_join_list_done",
        "    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;",
        "    move-result-object v5",
        "    return-object v5",
        ".end method",
        "",
        ".method public static joinTuple(Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;",
        "    .locals 7",
        "    new-instance v0, Ljava/lang/StringBuilder;",
        "    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V",
        "    if-nez p0, :ahnali_join_tuple_sep_ok",
        '    const-string p0, ""',
        "    :ahnali_join_tuple_sep_ok",
        "    if-eqz p1, :ahnali_join_tuple_done",
        "    array-length v1, p1",
        "    const/4 v2, 0x0",
        "    :ahnali_join_tuple_loop",
        "    if-ge v2, v1, :ahnali_join_tuple_done",
        "    if-lez v2, :ahnali_join_tuple_skip_sep",
        "    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;",
        "    move-result-object v0",
        "    :ahnali_join_tuple_skip_sep",
        "    aget-object v3, p1, v2",
        "    invoke-static {v3}, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;",
        "    move-result-object v4",
        "    invoke-virtual {v0, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;",
        "    move-result-object v0",
        "    add-int/lit8 v2, v2, 0x1",
        "    goto :ahnali_join_tuple_loop",
        "    :ahnali_join_tuple_done",
        "    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;",
        "    move-result-object v5",
        "    return-object v5",
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
        class_desc == "Lcom/ahnali/runtime/ReflectionRuntime;"
        and helper_method == "getText"
        and helper_sig == "(Landroid/widget/TextView;)Ljava/lang/String;"
    ):
        lines.extend(_emit_reflection_get_text_method())
        return "\n".join(lines)

    if (
        class_desc == "Lcom/ahnali/runtime/ListWrapperRuntime;"
        and helper_method == "create"
        and helper_sig == "()Ljava/util/ArrayList;"
    ):
        lines.extend(_emit_list_wrapper_runtime_methods())
        return "\n".join(lines)

    if (
        class_desc == "Lcom/ahnali/runtime/DictWrapperRuntime;"
        and helper_method == "create"
        and helper_sig == "()Ljava/util/HashMap;"
    ):
        lines.extend(_emit_dict_wrapper_runtime_methods())
        return "\n".join(lines)

    if (
        class_desc == "Lcom/ahnali/runtime/SetWrapperRuntime;"
        and helper_method == "create"
        and helper_sig == "()Ljava/util/HashSet;"
    ):
        lines.extend(_emit_set_wrapper_runtime_methods())
        return "\n".join(lines)

    if (
        class_desc == "Lcom/ahnali/runtime/TupleWrapperRuntime;"
        and helper_method == "create"
        and helper_sig == "(I)[Ljava/lang/Object;"
    ):
        lines.extend(_emit_tuple_wrapper_runtime_methods())
        return "\n".join(lines)

    if (
        class_desc == "Lcom/ahnali/runtime/StringMethodsRuntime;"
        and helper_method == "split"
        and helper_sig == "(Ljava/lang/String;Ljava/lang/String;)Ljava/util/ArrayList;"
    ):
        lines.extend(_emit_string_methods_runtime_methods())
        return "\n".join(lines)

    if append_service_helpers(
        lines=lines,
        class_desc=class_desc,
        helper_method=helper_method,
        helper_sig=helper_sig,
    ):
        return "\n".join(lines)

    if append_runtime_service_helpers(
        lines=lines,
        class_desc=class_desc,
        helper_method=helper_method,
        helper_sig=helper_sig,
    ):
        return "\n".join(lines)

    if append_networking_helpers(
        lines=lines,
        class_desc=class_desc,
        helper_method=helper_method,
        helper_sig=helper_sig,
    ):
        return "\n".join(lines)

    if append_storage_helpers(
        lines=lines,
        class_desc=class_desc,
        helper_method=helper_method,
        helper_sig=helper_sig,
    ):
        return "\n".join(lines)

    locals_count = 0 if ret_desc == "V" else 2 if ret_desc in {"J", "D"} else 1
    lines.append(f".method public static {helper_method}{helper_sig}")
    lines.append(f"    .locals {locals_count}")
    lines.extend(_emit_default_method_body(ret_desc))
    lines.append(".end method")
    return "\n".join(lines)

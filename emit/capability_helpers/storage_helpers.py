from __future__ import annotations

import re

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


def append_storage_helpers(*, lines: list[str], class_desc: str, helper_method: str, helper_sig: str) -> bool:
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
        return True

    return False

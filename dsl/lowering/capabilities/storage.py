from __future__ import annotations

from dsl.ir_helpers import assign, call, const, static_get, var


_STATE_BACKEND_METHODS = {
    "datastore": {
        "put": "dataStorePutString",
        "get": "dataStoreGetString",
        "remove": "dataStoreRemove",
        "exists": "dataStoreExists",
        "clear": "dataStoreClear",
    },
    "file": {
        "put": "fileWriteString",
        "get": "fileReadString",
        "remove": "fileRemove",
        "exists": "fileExists",
        "clear": "fileClear",
    },
    "sqlite": {
        "put": "sqlitePutString",
        "get": "sqliteGetString",
        "remove": "sqliteRemove",
        "exists": "sqliteExists",
        "clear": "sqliteClear",
    },
    "room": {
        "put": "roomPutString",
        "get": "roomGetString",
        "remove": "roomRemove",
        "exists": "roomExists",
        "clear": "roomClear",
    },
    "encrypted": {
        "put": "encryptedPutString",
        "get": "encryptedGetString",
        "remove": "encryptedRemove",
        "exists": "encryptedExists",
        "clear": "encryptedClear",
    },
}

_STATE_BACKEND_API_NAMES = {
    "datastore": {
        "put": "datastore_put",
        "get": "datastore_get",
        "remove": "datastore_remove",
        "exists": "datastore_exists",
        "clear": "datastore_clear",
    },
    "file": {
        "put": "file_write",
        "get": "file_read",
        "remove": "file_remove",
        "exists": "file_exists",
        "clear": "file_clear",
    },
    "sqlite": {
        "put": "sqlite_put",
        "get": "sqlite_get",
        "remove": "sqlite_remove",
        "exists": "sqlite_exists",
        "clear": "sqlite_clear",
    },
    "room": {
        "put": "room_put",
        "get": "room_get",
        "remove": "room_remove",
        "exists": "room_exists",
        "clear": "room_clear",
    },
    "encrypted": {
        "put": "encrypted_storage_put",
        "get": "encrypted_storage_get",
        "remove": "encrypted_storage_remove",
        "exists": "encrypted_storage_exists",
        "clear": "encrypted_storage_clear",
    },
}


class CapabilityStorageLoweringMixin:
    def _compile_storage_put_stmt(self, stmt):
        binding = self._require_helper_capability(
            api_name="storage_put",
            capability_name="Storage",
            require_helper_method=True,
        )
        result_tmp = self._next_tmp("storage_put_result")
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    binding.helper_method,
                    args=[var("ctx"), const(str(stmt.key)), const(str(stmt.value))],
                    return_type="I",
                    arg_types=[
                        "Landroid/app/Activity;",
                        "Ljava/lang/String;",
                        "Ljava/lang/String;",
                    ],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ]

    def _compile_storage_get_call(self, *, key: str, default_value: str, tmp_prefix: str):
        binding = self._require_helper_capability(
            api_name="storage_get",
            capability_name="Storage",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "getString",
                    args=[var("ctx"), const(str(key)), const(str(default_value))],
                    return_type="Ljava/lang/String;",
                    arg_types=[
                        "Landroid/app/Activity;",
                        "Ljava/lang/String;",
                        "Ljava/lang/String;",
                    ],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_storage_get_stmt(self, stmt):
        out, _ = self._compile_storage_get_call(
            key=stmt.key,
            default_value=stmt.default_value,
            tmp_prefix="storage_get_ignored",
        )
        return out

    def _compile_storage_exists_call(self, *, key: str, tmp_prefix: str):
        binding = self._require_helper_capability(
            api_name="storage_exists",
            capability_name="Storage",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "exists",
                    args=[var("ctx"), const(str(key))],
                    return_type="I",
                    arg_types=[
                        "Landroid/app/Activity;",
                        "Ljava/lang/String;",
                    ],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_storage_exists_stmt(self, stmt):
        out, _ = self._compile_storage_exists_call(
            key=stmt.key,
            tmp_prefix="storage_exists_ignored",
        )
        return out

    def _compile_storage_remove_stmt(self, stmt):
        binding = self._require_helper_capability(
            api_name="storage_remove",
            capability_name="Storage",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp("storage_remove_result")
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "remove",
                    args=[var("ctx"), const(str(stmt.key))],
                    return_type="I",
                    arg_types=[
                        "Landroid/app/Activity;",
                        "Ljava/lang/String;",
                    ],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ]

    def _compile_storage_clear_stmt(self, stmt):
        binding = self._require_helper_capability(
            api_name="storage_clear",
            capability_name="Storage",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp("storage_clear_result")
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "clear",
                    args=[var("ctx")],
                    return_type="I",
                    arg_types=[
                        "Landroid/app/Activity;",
                    ],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ]

    def _state_backend_contract(self, *, backend: str, op: str):
        backend_key = str(backend or "").strip().lower()
        methods = _STATE_BACKEND_METHODS.get(backend_key)
        api_names = _STATE_BACKEND_API_NAMES.get(backend_key)
        if methods is None or api_names is None:
            raise RuntimeError(f"Unsupported state backend '{backend}'.")
        method_name = methods.get(op)
        api_name = api_names.get(op)
        if not method_name or not api_name:
            raise RuntimeError(f"Unsupported state backend operation '{backend_key}:{op}'.")
        return api_name, method_name

    def _compile_state_backend_put_stmt(self, stmt):
        api_name, method_name = self._state_backend_contract(backend=stmt.backend, op="put")
        binding = self._require_helper_capability(
            api_name=api_name,
            capability_name="Storage",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(f"{stmt.backend}_put_result")
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    method_name,
                    args=[var("ctx"), const(str(stmt.key)), const(str(stmt.value))],
                    return_type="I",
                    arg_types=[
                        "Landroid/app/Activity;",
                        "Ljava/lang/String;",
                        "Ljava/lang/String;",
                    ],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ]

    def _compile_state_backend_get_call(self, *, backend: str, key: str, default_value: str, tmp_prefix: str):
        api_name, method_name = self._state_backend_contract(backend=backend, op="get")
        binding = self._require_helper_capability(
            api_name=api_name,
            capability_name="Storage",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    method_name,
                    args=[var("ctx"), const(str(key)), const(str(default_value))],
                    return_type="Ljava/lang/String;",
                    arg_types=[
                        "Landroid/app/Activity;",
                        "Ljava/lang/String;",
                        "Ljava/lang/String;",
                    ],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_state_backend_get_stmt(self, stmt):
        out, _ = self._compile_state_backend_get_call(
            backend=stmt.backend,
            key=stmt.key,
            default_value=stmt.default_value,
            tmp_prefix=f"{stmt.backend}_get_ignored",
        )
        return out

    def _compile_state_backend_exists_call(self, *, backend: str, key: str, tmp_prefix: str):
        api_name, method_name = self._state_backend_contract(backend=backend, op="exists")
        binding = self._require_helper_capability(
            api_name=api_name,
            capability_name="Storage",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    method_name,
                    args=[var("ctx"), const(str(key))],
                    return_type="I",
                    arg_types=[
                        "Landroid/app/Activity;",
                        "Ljava/lang/String;",
                    ],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_state_backend_exists_stmt(self, stmt):
        out, _ = self._compile_state_backend_exists_call(
            backend=stmt.backend,
            key=stmt.key,
            tmp_prefix=f"{stmt.backend}_exists_ignored",
        )
        return out

    def _compile_state_backend_remove_stmt(self, stmt):
        api_name, method_name = self._state_backend_contract(backend=stmt.backend, op="remove")
        binding = self._require_helper_capability(
            api_name=api_name,
            capability_name="Storage",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(f"{stmt.backend}_remove_result")
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    method_name,
                    args=[var("ctx"), const(str(stmt.key))],
                    return_type="I",
                    arg_types=[
                        "Landroid/app/Activity;",
                        "Ljava/lang/String;",
                    ],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ]

    def _compile_state_backend_clear_stmt(self, stmt):
        api_name, method_name = self._state_backend_contract(backend=stmt.backend, op="clear")
        binding = self._require_helper_capability(
            api_name=api_name,
            capability_name="Storage",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(f"{stmt.backend}_clear_result")
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    method_name,
                    args=[var("ctx")],
                    return_type="I",
                    arg_types=[
                        "Landroid/app/Activity;",
                    ],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ]

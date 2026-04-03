from __future__ import annotations

from dsl.ir_helpers import assign, call, call_stmt, compare, const, if_, new, static_get, var


class CapabilityNetworkingLoweringMixin:
    def _compile_http_get_call(self, *, url: str, default_value: str, tmp_prefix: str):
        binding = self._require_helper_capability(
            api_name="http_get",
            capability_name="Networking",
            require_helper_method=True,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    binding.helper_method,
                    args=[var("ctx"), const(str(url)), const(str(default_value))],
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

    def _compile_http_get_status_call(self, *, url: str, tmp_prefix: str):
        binding = self._require_helper_capability(
            api_name="http_get_status",
            capability_name="Networking",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "httpGetStatus",
                    args=[var("ctx"), const(str(url))],
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

    def _compile_http_get_error_call(self, *, url: str, tmp_prefix: str):
        binding = self._require_helper_capability(
            api_name="http_get_error",
            capability_name="Networking",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "httpGetError",
                    args=[var("ctx"), const(str(url))],
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

    def _compile_http_get_retry_call(
        self,
        *,
        url: str,
        retries: int,
        backoff_ms: int,
        default_value: str,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name="http_get_retry",
            capability_name="Networking",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "httpGetRetry",
                    args=[
                        var("ctx"),
                        const(str(url)),
                        const(int(retries)),
                        const(int(backoff_ms)),
                        const(str(default_value)),
                    ],
                    return_type="Ljava/lang/String;",
                    arg_types=[
                        "Landroid/app/Activity;",
                        "Ljava/lang/String;",
                        "I",
                        "I",
                        "Ljava/lang/String;",
                    ],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_http_get_json_field_call(
        self,
        *,
        url: str,
        key: str,
        fallback: str,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name="http_get_json_field",
            capability_name="Networking",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "httpGetJsonField",
                    args=[var("ctx"), const(str(url)), const(str(key)), const(str(fallback))],
                    return_type="Ljava/lang/String;",
                    arg_types=[
                        "Landroid/app/Activity;",
                        "Ljava/lang/String;",
                        "Ljava/lang/String;",
                        "Ljava/lang/String;",
                    ],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_http_get_json_field_error_call(
        self,
        *,
        url: str,
        key: str,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name="http_get_json_field_error",
            capability_name="Networking",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "httpGetJsonFieldError",
                    args=[var("ctx"), const(str(url)), const(str(key))],
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
        ], var(result_tmp)

    def _compile_http_get_stmt(self, stmt):
        out, _ = self._compile_http_get_call(
            url=stmt.url,
            default_value=stmt.default_value,
            tmp_prefix="http_get_ignored",
        )
        return out

    def _compile_http_get_status_stmt(self, stmt):
        out, _ = self._compile_http_get_status_call(
            url=stmt.url,
            tmp_prefix="http_get_status_ignored",
        )
        return out

    def _compile_http_get_error_stmt(self, stmt):
        out, _ = self._compile_http_get_error_call(
            url=stmt.url,
            tmp_prefix="http_get_error_ignored",
        )
        return out

    def _compile_http_get_retry_stmt(self, stmt):
        out, _ = self._compile_http_get_retry_call(
            url=stmt.url,
            retries=stmt.retries,
            backoff_ms=stmt.backoff_ms,
            default_value=stmt.default_value,
            tmp_prefix="http_get_retry_ignored",
        )
        return out

    def _compile_http_get_json_field_stmt(self, stmt):
        out, _ = self._compile_http_get_json_field_call(
            url=stmt.url,
            key=stmt.key,
            fallback=stmt.fallback,
            tmp_prefix="http_get_json_field_ignored",
        )
        return out

    def _compile_http_get_json_field_error_stmt(self, stmt):
        out, _ = self._compile_http_get_json_field_error_call(
            url=stmt.url,
            key=stmt.key,
            tmp_prefix="http_get_json_field_error_ignored",
        )
        return out

    def _compile_http_get_route_stmt(self, stmt):
        if getattr(self, "_current_event_kind", None) != "click":
            raise RuntimeError(
                "http_get_route is only supported inside @on_click handlers. "
                "Fix: move http_get_route(...) into an @on_click(...) handler."
            )
        known_targets = getattr(self, "_click_event_targets", set())
        for target_id, role in (
            (stmt.success_target_id, "success_target_id"),
            (stmt.failure_target_id, "failure_target_id"),
        ):
            if target_id not in known_targets:
                raise RuntimeError(
                    f"http_get_route argument '{role}' references unknown on_click target '{target_id}'. "
                    f"Fix: add @on_click('{target_id}') handler in the same activity."
                )
        status_prefix, status_expr = self._compile_http_get_status_call(
            url=stmt.url,
            tmp_prefix="http_get_route_status",
        )
        body_prefix, _ = self._compile_http_get_call(
            url=stmt.url,
            default_value=stmt.default_value,
            tmp_prefix="http_get_route_body",
        )
        error_prefix, _ = self._compile_http_get_error_call(
            url=stmt.url,
            tmp_prefix="http_get_route_error",
        )
        owner = getattr(self, "_handler_owner_desc", "LTestHandlers;")
        return [
            *status_prefix,
            *body_prefix,
            *error_prefix,
            if_(
                compare("==", status_expr, const(200)),
                [
                    call_stmt(
                        f"onClick_{stmt.success_target_id}",
                        args=[var("view")],
                        return_type=None,
                        arg_types=["Landroid/view/View;"],
                        invoke_kind="static",
                        owner=owner,
                    )
                ],
                [
                    call_stmt(
                        f"onClick_{stmt.failure_target_id}",
                        args=[var("view")],
                        return_type=None,
                        arg_types=["Landroid/view/View;"],
                        invoke_kind="static",
                        owner=owner,
                    )
                ],
            ),
        ]

    def _compile_http_get_route_async_call(
        self,
        *,
        url: str,
        success_target_id: str,
        failure_target_id: str,
        default_value: str,
        progress_target_id: str,
        retries: int,
        timeout_ms: int,
        method: str,
        headers: str,
        body: str,
        tmp_prefix: str,
    ):
        if getattr(self, "_current_event_kind", None) != "click":
            raise RuntimeError(
                "http_get_route_async is only supported inside @on_click handlers. "
                "Fix: move http_get_route_async(...) into an @on_click(...) handler."
            )
        known_targets = getattr(self, "_click_event_targets", set())
        for target_id, role in (
            (success_target_id, "success_target_id"),
            (failure_target_id, "failure_target_id"),
        ):
            if target_id not in known_targets:
                raise RuntimeError(
                    f"http_get_route_async argument '{role}' references unknown on_click target '{target_id}'. "
                    f"Fix: add @on_click('{target_id}') handler in the same activity."
                )
        if progress_target_id and progress_target_id not in known_targets:
            raise RuntimeError(
                "http_get_route_async argument 'progress_target_id' references unknown on_click target "
                f"'{progress_target_id}'. Fix: add @on_click('{progress_target_id}') handler in the same activity."
            )

        binding = self._require_helper_capability(
            api_name="http_get_route_async",
            capability_name="Networking",
            require_helper_method=False,
        )
        owner = getattr(self, "_handler_owner_desc", "LTestHandlers;")
        success_runnable_desc = f"Lcom/ahnali/preview/AhnaliUiRunnable_{success_target_id};"
        failure_runnable_desc = f"Lcom/ahnali/preview/AhnaliUiRunnable_{failure_target_id};"
        worker_desc = "Lcom/ahnali/preview/AhnaliHttpRouteAsyncWorker;"

        self._queue_support_class(
            success_runnable_desc,
            f"onClick_{success_target_id}",
            owner,
            "ui_runnable_click",
        )
        self._queue_support_class(
            failure_runnable_desc,
            f"onClick_{failure_target_id}",
            owner,
            "ui_runnable_click",
        )
        if progress_target_id:
            progress_runnable_desc = f"Lcom/ahnali/preview/AhnaliUiRunnable_{progress_target_id};"
            self._queue_support_class(
                progress_runnable_desc,
                f"onClick_{progress_target_id}",
                owner,
                "ui_runnable_click",
            )
        else:
            progress_runnable_desc = ""
        self._queue_support_class(
            worker_desc,
            "",
            owner,
            "http_route_async_worker",
        )

        success_tmp = self._next_tmp("http_route_async_success")
        failure_tmp = self._next_tmp("http_route_async_failure")
        progress_tmp = self._next_tmp("http_route_async_progress")
        token_tmp = self._next_tmp("http_route_async_token")
        worker_tmp = self._next_tmp("http_route_async_worker")
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                success_tmp,
                new(
                    success_runnable_desc,
                    args=[var("view")],
                    arg_types=["Landroid/view/View;"],
                ),
            ),
            assign(
                failure_tmp,
                new(
                    failure_runnable_desc,
                    args=[var("view")],
                    arg_types=["Landroid/view/View;"],
                ),
            ),
            assign(
                progress_tmp,
                new(
                    progress_runnable_desc,
                    args=[var("view")],
                    arg_types=["Landroid/view/View;"],
                ),
            )
            if progress_runnable_desc
            else assign(progress_tmp, const(0)),
            assign(
                token_tmp,
                call(
                    "nextAsyncToken",
                    args=[],
                    return_type="I",
                    arg_types=[],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
            assign(
                worker_tmp,
                new(
                    worker_desc,
                    args=[
                        var("ctx"),
                        const(str(url)),
                        const(str(default_value)),
                        const(str(method)),
                        const(str(headers)),
                        const(str(body)),
                        var(success_tmp),
                        var(failure_tmp),
                        var(progress_tmp),
                        var(token_tmp),
                        const(int(retries)),
                        const(int(timeout_ms)),
                    ],
                    arg_types=[
                        "Landroid/app/Activity;",
                        "Ljava/lang/String;",
                        "Ljava/lang/String;",
                        "Ljava/lang/String;",
                        "Ljava/lang/String;",
                        "Ljava/lang/String;",
                        "Ljava/lang/Runnable;",
                        "Ljava/lang/Runnable;",
                        "Ljava/lang/Runnable;",
                        "I",
                        "I",
                        "I",
                    ],
                ),
            ),
            assign(
                result_tmp,
                call(
                    "startAsyncWithToken",
                    args=[var(token_tmp), var(worker_tmp)],
                    return_type="I",
                    arg_types=["I", "Ljava/lang/Runnable;"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_http_get_route_async_stmt(self, stmt):
        out, _ = self._compile_http_get_route_async_call(
            url=stmt.url,
            success_target_id=stmt.success_target_id,
            failure_target_id=stmt.failure_target_id,
            default_value=stmt.default_value,
            progress_target_id=getattr(stmt, "progress_target_id", ""),
            retries=int(getattr(stmt, "retries", 0)),
            timeout_ms=int(getattr(stmt, "timeout_ms", 8000)),
            method=str(getattr(stmt, "method", "GET")),
            headers=str(getattr(stmt, "headers", "")),
            body=str(getattr(stmt, "body", "")),
            tmp_prefix="http_get_route_async_ignored",
        )
        return out

    def _compile_http_async_token_value(self, *, token_expr, owner: str, tmp_prefix: str):
        if token_expr is None:
            token_tmp = self._next_tmp(tmp_prefix)
            return [
                assign(
                    token_tmp,
                    call(
                        "getCurrentAsyncToken",
                        args=[],
                        return_type="I",
                        arg_types=[],
                        invoke_kind="static",
                        owner=owner,
                    ),
                )
            ], var(token_tmp)
        return self._compile_int_expr(token_expr)

    def _compile_http_async_cancel_call(self, *, token_expr, tmp_prefix: str):
        binding = self._require_helper_capability(
            api_name="http_async_cancel",
            capability_name="Networking",
            require_helper_method=False,
        )
        token_prefix, token_value = self._compile_http_async_token_value(
            token_expr=token_expr,
            owner=binding.helper_class_desc,
            tmp_prefix="http_async_token_cancel",
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            *token_prefix,
            assign(
                result_tmp,
                call(
                    "cancelAsync",
                    args=[token_value],
                    return_type="I",
                    arg_types=["I"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_http_async_progress_call(self, *, token_expr, tmp_prefix: str):
        binding = self._require_helper_capability(
            api_name="http_async_progress",
            capability_name="Networking",
            require_helper_method=False,
        )
        token_prefix, token_value = self._compile_http_async_token_value(
            token_expr=token_expr,
            owner=binding.helper_class_desc,
            tmp_prefix="http_async_token_progress",
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            *token_prefix,
            assign(
                result_tmp,
                call(
                    "getAsyncProgress",
                    args=[token_value],
                    return_type="I",
                    arg_types=["I"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_http_async_error_call(self, *, token_expr, tmp_prefix: str):
        binding = self._require_helper_capability(
            api_name="http_async_error",
            capability_name="Networking",
            require_helper_method=False,
        )
        token_prefix, token_value = self._compile_http_async_token_value(
            token_expr=token_expr,
            owner=binding.helper_class_desc,
            tmp_prefix="http_async_token_error",
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            *token_prefix,
            assign(
                result_tmp,
                call(
                    "getAsyncError",
                    args=[token_value],
                    return_type="I",
                    arg_types=["I"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_http_async_status_call(self, *, token_expr, tmp_prefix: str):
        binding = self._require_helper_capability(
            api_name="http_async_status",
            capability_name="Networking",
            require_helper_method=False,
        )
        token_prefix, token_value = self._compile_http_async_token_value(
            token_expr=token_expr,
            owner=binding.helper_class_desc,
            tmp_prefix="http_async_token_status",
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            *token_prefix,
            assign(
                result_tmp,
                call(
                    "getAsyncStatus",
                    args=[token_value],
                    return_type="I",
                    arg_types=["I"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_http_async_body_call(self, *, token_expr, fallback: str, tmp_prefix: str):
        binding = self._require_helper_capability(
            api_name="http_async_body",
            capability_name="Networking",
            require_helper_method=False,
        )
        token_prefix, token_value = self._compile_http_async_token_value(
            token_expr=token_expr,
            owner=binding.helper_class_desc,
            tmp_prefix="http_async_token_body",
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            *token_prefix,
            assign(
                result_tmp,
                call(
                    "getAsyncBody",
                    args=[token_value, const(str(fallback))],
                    return_type="Ljava/lang/String;",
                    arg_types=["I", "Ljava/lang/String;"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_http_async_json_field_call(self, *, token_expr, key: str, fallback: str, tmp_prefix: str):
        binding = self._require_helper_capability(
            api_name="http_async_json_field",
            capability_name="Networking",
            require_helper_method=False,
        )
        token_prefix, token_value = self._compile_http_async_token_value(
            token_expr=token_expr,
            owner=binding.helper_class_desc,
            tmp_prefix="http_async_token_json_field",
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            *token_prefix,
            assign(
                result_tmp,
                call(
                    "getAsyncJsonField",
                    args=[token_value, const(str(key)), const(str(fallback))],
                    return_type="Ljava/lang/String;",
                    arg_types=["I", "Ljava/lang/String;", "Ljava/lang/String;"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_http_async_json_field_error_call(self, *, token_expr, key: str, tmp_prefix: str):
        binding = self._require_helper_capability(
            api_name="http_async_json_field_error",
            capability_name="Networking",
            require_helper_method=False,
        )
        token_prefix, token_value = self._compile_http_async_token_value(
            token_expr=token_expr,
            owner=binding.helper_class_desc,
            tmp_prefix="http_async_token_json_field_error",
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            *token_prefix,
            assign(
                result_tmp,
                call(
                    "getAsyncJsonFieldError",
                    args=[token_value, const(str(key))],
                    return_type="I",
                    arg_types=["I", "Ljava/lang/String;"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_http_async_json_array_length_call(self, *, token_expr, fallback: int, tmp_prefix: str):
        binding = self._require_helper_capability(
            api_name="http_async_json_array_length",
            capability_name="Networking",
            require_helper_method=False,
        )
        token_prefix, token_value = self._compile_http_async_token_value(
            token_expr=token_expr,
            owner=binding.helper_class_desc,
            tmp_prefix="http_async_token_json_array_length",
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            *token_prefix,
            assign(
                result_tmp,
                call(
                    "getAsyncJsonArrayLength",
                    args=[token_value, const(int(fallback))],
                    return_type="I",
                    arg_types=["I", "I"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_http_async_cancel_stmt(self, stmt):
        out, _ = self._compile_http_async_cancel_call(
            token_expr=getattr(stmt, "token", None),
            tmp_prefix="http_async_cancel_ignored",
        )
        return out

    def _compile_http_async_progress_stmt(self, stmt):
        out, _ = self._compile_http_async_progress_call(
            token_expr=getattr(stmt, "token", None),
            tmp_prefix="http_async_progress_ignored",
        )
        return out

    def _compile_http_async_error_stmt(self, stmt):
        out, _ = self._compile_http_async_error_call(
            token_expr=getattr(stmt, "token", None),
            tmp_prefix="http_async_error_ignored",
        )
        return out

    def _compile_http_async_status_stmt(self, stmt):
        out, _ = self._compile_http_async_status_call(
            token_expr=getattr(stmt, "token", None),
            tmp_prefix="http_async_status_ignored",
        )
        return out

    def _compile_http_async_body_stmt(self, stmt):
        out, _ = self._compile_http_async_body_call(
            token_expr=getattr(stmt, "token", None),
            fallback=getattr(stmt, "fallback", ""),
            tmp_prefix="http_async_body_ignored",
        )
        return out

    def _compile_http_async_json_field_stmt(self, stmt):
        out, _ = self._compile_http_async_json_field_call(
            token_expr=getattr(stmt, "token", None),
            key=getattr(stmt, "key", ""),
            fallback=getattr(stmt, "fallback", ""),
            tmp_prefix="http_async_json_field_ignored",
        )
        return out

    def _compile_http_async_json_field_error_stmt(self, stmt):
        out, _ = self._compile_http_async_json_field_error_call(
            token_expr=getattr(stmt, "token", None),
            key=getattr(stmt, "key", ""),
            tmp_prefix="http_async_json_field_error_ignored",
        )
        return out

    def _compile_http_async_json_array_length_stmt(self, stmt):
        out, _ = self._compile_http_async_json_array_length_call(
            token_expr=getattr(stmt, "token", None),
            fallback=int(getattr(stmt, "fallback", 0)),
            tmp_prefix="http_async_json_array_length_ignored",
        )
        return out

from __future__ import annotations

from dsl.ir_helpers import assign, call, call_stmt, compare, const, if_, new, static_get, var


class CapabilityServiceLoweringMixin:
    def _compile_clipboard_set_call(
        self,
        *,
        text: str,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name="clipboard_set",
            capability_name="Clipboard",
            require_helper_method=True,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    binding.helper_method,
                    args=[var("ctx"), const(str(text))],
                    return_type="I",
                    arg_types=["Landroid/app/Activity;", "Ljava/lang/String;"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_clipboard_get_call(
        self,
        *,
        fallback: str,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name="clipboard_get",
            capability_name="Clipboard",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "getText",
                    args=[var("ctx"), const(str(fallback))],
                    return_type="Ljava/lang/String;",
                    arg_types=["Landroid/app/Activity;", "Ljava/lang/String;"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_deep_link_get_call(
        self,
        *,
        fallback: str,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name="deep_link_get",
            capability_name="DeepLinking",
            require_helper_method=True,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    binding.helper_method,
                    args=[var("ctx"), const(str(fallback))],
                    return_type="Ljava/lang/String;",
                    arg_types=["Landroid/app/Activity;", "Ljava/lang/String;"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_deep_link_error_call(
        self,
        *,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name="deep_link_error",
            capability_name="DeepLinking",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "getLaunchUriError",
                    args=[var("ctx")],
                    return_type="I",
                    arg_types=["Landroid/app/Activity;"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_work_status_call(
        self,
        *,
        name: str,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name="work_status",
            capability_name="WorkManager",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "getWorkStatus",
                    args=[var("ctx"), const(str(name))],
                    return_type="I",
                    arg_types=["Landroid/app/Activity;", "Ljava/lang/String;"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_work_error_call(
        self,
        *,
        name: str,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name="work_error",
            capability_name="WorkManager",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "getWorkStatusError",
                    args=[var("ctx"), const(str(name))],
                    return_type="I",
                    arg_types=["Landroid/app/Activity;", "Ljava/lang/String;"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_work_enqueue_stmt(self, stmt):
        binding = self._require_helper_capability(
            api_name="work_enqueue",
            capability_name="WorkManager",
            require_helper_method=True,
        )
        result_tmp = self._next_tmp("work_enqueue_result")
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    binding.helper_method,
                    args=[
                        var("ctx"),
                        const(str(getattr(stmt, "name", ""))),
                        const(int(getattr(stmt, "delay_seconds", 0) or 0)),
                    ],
                    return_type="I",
                    arg_types=["Landroid/app/Activity;", "Ljava/lang/String;", "I"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ]

    def _compile_work_cancel_stmt(self, stmt):
        binding = self._require_helper_capability(
            api_name="work_cancel",
            capability_name="WorkManager",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp("work_cancel_result")
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "cancelWork",
                    args=[var("ctx"), const(str(getattr(stmt, "name", "")))],
                    return_type="I",
                    arg_types=["Landroid/app/Activity;", "Ljava/lang/String;"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ]

    def _compile_alarm_status_call(
        self,
        *,
        name: str,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name="alarm_status",
            capability_name="AlarmManager",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "getAlarmStatus",
                    args=[var("ctx"), const(str(name))],
                    return_type="I",
                    arg_types=["Landroid/app/Activity;", "Ljava/lang/String;"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_alarm_error_call(
        self,
        *,
        name: str,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name="alarm_error",
            capability_name="AlarmManager",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "getAlarmStatusError",
                    args=[var("ctx"), const(str(name))],
                    return_type="I",
                    arg_types=["Landroid/app/Activity;", "Ljava/lang/String;"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_alarm_schedule_stmt(self, stmt):
        binding = self._require_helper_capability(
            api_name="alarm_schedule",
            capability_name="AlarmManager",
            require_helper_method=True,
        )
        result_tmp = self._next_tmp("alarm_schedule_result")
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    binding.helper_method,
                    args=[
                        var("ctx"),
                        const(str(getattr(stmt, "name", ""))),
                        const(int(getattr(stmt, "trigger_seconds", 0) or 0)),
                    ],
                    return_type="I",
                    arg_types=["Landroid/app/Activity;", "Ljava/lang/String;", "I"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ]

    def _compile_alarm_cancel_stmt(self, stmt):
        binding = self._require_helper_capability(
            api_name="alarm_cancel",
            capability_name="AlarmManager",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp("alarm_cancel_result")
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "cancelAlarm",
                    args=[var("ctx"), const(str(getattr(stmt, "name", "")))],
                    return_type="I",
                    arg_types=["Landroid/app/Activity;", "Ljava/lang/String;"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ]

    def _compile_job_status_call(
        self,
        *,
        job_id: int,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name="job_status",
            capability_name="JobScheduler",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "getJobStatus",
                    args=[var("ctx"), const(int(job_id))],
                    return_type="I",
                    arg_types=["Landroid/app/Activity;", "I"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_job_error_call(
        self,
        *,
        job_id: int,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name="job_error",
            capability_name="JobScheduler",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "getJobStatusError",
                    args=[var("ctx"), const(int(job_id))],
                    return_type="I",
                    arg_types=["Landroid/app/Activity;", "I"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_job_schedule_stmt(self, stmt):
        binding = self._require_helper_capability(
            api_name="job_schedule",
            capability_name="JobScheduler",
            require_helper_method=True,
        )
        result_tmp = self._next_tmp("job_schedule_result")
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    binding.helper_method,
                    args=[
                        var("ctx"),
                        const(int(getattr(stmt, "job_id", 0) or 0)),
                        const(int(getattr(stmt, "delay_seconds", 0) or 0)),
                    ],
                    return_type="I",
                    arg_types=["Landroid/app/Activity;", "I", "I"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ]

    def _compile_job_cancel_stmt(self, stmt):
        binding = self._require_helper_capability(
            api_name="job_cancel",
            capability_name="JobScheduler",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp("job_cancel_result")
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "cancelJob",
                    args=[var("ctx"), const(int(getattr(stmt, "job_id", 0) or 0))],
                    return_type="I",
                    arg_types=["Landroid/app/Activity;", "I"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ]

    def _compile_clipboard_set_stmt(self, stmt):
        out, _ = self._compile_clipboard_set_call(
            text=getattr(stmt, "text", ""),
            tmp_prefix="clipboard_set_ignored",
        )
        return out

    def _compile_share_text_result_call(
        self,
        *,
        api_name: str = "share_text_result",
        text: str,
        chooser_title: str,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name=api_name,
            capability_name="Sharing",
            require_helper_method=True,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    binding.helper_method,
                    args=[var("ctx"), const(str(text)), const(str(chooser_title))],
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

    def _compile_share_text_error_call(
        self,
        *,
        text: str,
        chooser_title: str,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name="share_text_error",
            capability_name="Sharing",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "shareTextError",
                    args=[var("ctx"), const(str(text)), const(str(chooser_title))],
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

    def _compile_share_file_result_call(
        self,
        *,
        api_name: str = "share_file_result",
        uri: str,
        chooser_title: str,
        mime_type: str,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name=api_name,
            capability_name="Sharing",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "shareFile",
                    args=[var("ctx"), const(str(uri)), const(str(chooser_title)), const(str(mime_type))],
                    return_type="I",
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

    def _compile_share_file_error_call(
        self,
        *,
        uri: str,
        chooser_title: str,
        mime_type: str,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name="share_file_error",
            capability_name="Sharing",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "shareFileError",
                    args=[var("ctx"), const(str(uri)), const(str(chooser_title)), const(str(mime_type))],
                    return_type="I",
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

    def _compile_open_external_call(
        self,
        *,
        api_name: str = "open_external",
        uri: str,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name=api_name,
            capability_name="Sharing",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "openUri",
                    args=[var("ctx"), const(str(uri))],
                    return_type="I",
                    arg_types=["Landroid/app/Activity;", "Ljava/lang/String;"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_open_external_error_call(
        self,
        *,
        uri: str,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name="open_external_error",
            capability_name="Sharing",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "openUriError",
                    args=[var("ctx"), const(str(uri))],
                    return_type="I",
                    arg_types=["Landroid/app/Activity;", "Ljava/lang/String;"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_share_text_stmt(self, stmt):
        out, _ = self._compile_share_text_result_call(
            api_name="share_text",
            text=getattr(stmt, "text", ""),
            chooser_title=getattr(stmt, "chooser_title", "Share via"),
            tmp_prefix="share_text_ignored",
        )
        return out

    def _compile_share_file_stmt(self, stmt):
        out, _ = self._compile_share_file_result_call(
            api_name="share_file",
            uri=getattr(stmt, "uri", ""),
            chooser_title=getattr(stmt, "chooser_title", "Share file via"),
            mime_type=getattr(stmt, "mime_type", "*/*"),
            tmp_prefix="share_file_ignored",
        )
        return out

    def _compile_open_external_stmt(self, stmt):
        out, _ = self._compile_open_external_call(
            api_name="open_external",
            uri=getattr(stmt, "uri", ""),
            tmp_prefix="open_external_ignored",
        )
        return out

    def _compile_web_set_policy_call(
        self,
        *,
        api_name: str = "web_set_policy",
        js_enabled: int,
        dom_storage: int,
        allow_file_access: int,
        allow_cleartext: int,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name=api_name,
            capability_name="WebView",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "setPolicy",
                    args=[
                        var("ctx"),
                        const(int(js_enabled)),
                        const(int(dom_storage)),
                        const(int(allow_file_access)),
                        const(int(allow_cleartext)),
                    ],
                    return_type="I",
                    arg_types=[
                        "Landroid/app/Activity;",
                        "I",
                        "I",
                        "I",
                        "I",
                    ],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_web_load_result_call(
        self,
        *,
        api_name: str = "web_load_result",
        url: str,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name=api_name,
            capability_name="WebView",
            require_helper_method=True,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    binding.helper_method,
                    args=[var("ctx"), const(str(url))],
                    return_type="I",
                    arg_types=["Landroid/app/Activity;", "Ljava/lang/String;"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_web_load_error_call(
        self,
        *,
        url: str,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name="web_load_error",
            capability_name="WebView",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "loadUrlError",
                    args=[var("ctx"), const(str(url))],
                    return_type="I",
                    arg_types=["Landroid/app/Activity;", "Ljava/lang/String;"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_web_add_js_bridge_result_call(
        self,
        *,
        api_name: str = "web_add_js_bridge_result",
        bridge_name: str,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name=api_name,
            capability_name="WebView",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "addJsBridge",
                    args=[var("ctx"), const(str(bridge_name))],
                    return_type="I",
                    arg_types=["Landroid/app/Activity;", "Ljava/lang/String;"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_web_add_js_bridge_error_call(
        self,
        *,
        bridge_name: str,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name="web_add_js_bridge_error",
            capability_name="WebView",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "addJsBridgeError",
                    args=[var("ctx"), const(str(bridge_name))],
                    return_type="I",
                    arg_types=["Landroid/app/Activity;", "Ljava/lang/String;"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_web_set_policy_stmt(self, stmt):
        out, _ = self._compile_web_set_policy_call(
            api_name="web_set_policy",
            js_enabled=getattr(stmt, "js_enabled", 0),
            dom_storage=getattr(stmt, "dom_storage", 0),
            allow_file_access=getattr(stmt, "allow_file_access", 0),
            allow_cleartext=getattr(stmt, "allow_cleartext", 0),
            tmp_prefix="web_set_policy_ignored",
        )
        return out

    def _compile_web_load_stmt(self, stmt):
        out, _ = self._compile_web_load_result_call(
            api_name="web_load",
            url=getattr(stmt, "url", ""),
            tmp_prefix="web_load_ignored",
        )
        return out

    def _compile_web_add_js_bridge_stmt(self, stmt):
        out, _ = self._compile_web_add_js_bridge_result_call(
            api_name="web_add_js_bridge",
            bridge_name=getattr(stmt, "bridge_name", ""),
            tmp_prefix="web_add_js_bridge_ignored",
        )
        return out

    def _compile_web_choose_file_result_call(
        self,
        *,
        api_name: str = "web_choose_file_result",
        mime_type: str,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name=api_name,
            capability_name="WebView",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "chooseFile",
                    args=[var("ctx"), const(str(mime_type))],
                    return_type="I",
                    arg_types=["Landroid/app/Activity;", "Ljava/lang/String;"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_web_choose_file_error_call(
        self,
        *,
        mime_type: str,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name="web_choose_file_error",
            capability_name="WebView",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "chooseFileError",
                    args=[var("ctx"), const(str(mime_type))],
                    return_type="I",
                    arg_types=["Landroid/app/Activity;", "Ljava/lang/String;"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_web_cookie_set_result_call(
        self,
        *,
        api_name: str = "web_cookie_set_result",
        url: str,
        cookie: str,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name=api_name,
            capability_name="WebView",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "setCookie",
                    args=[var("ctx"), const(str(url)), const(str(cookie))],
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

    def _compile_web_cookie_set_error_call(
        self,
        *,
        url: str,
        cookie: str,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name="web_cookie_set_error",
            capability_name="WebView",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "setCookieError",
                    args=[var("ctx"), const(str(url)), const(str(cookie))],
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

    def _compile_web_cookie_get_call(
        self,
        *,
        url: str,
        fallback: str,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name="web_cookie_get",
            capability_name="WebView",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "getCookie",
                    args=[var("ctx"), const(str(url)), const(str(fallback))],
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

    def _compile_web_cookie_get_error_call(
        self,
        *,
        url: str,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name="web_cookie_get_error",
            capability_name="WebView",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "getCookieError",
                    args=[var("ctx"), const(str(url))],
                    return_type="I",
                    arg_types=["Landroid/app/Activity;", "Ljava/lang/String;"],
                    invoke_kind="static",
                    owner=binding.helper_class_desc,
                ),
            ),
        ], var(result_tmp)

    def _compile_web_choose_file_stmt(self, stmt):
        out, _ = self._compile_web_choose_file_result_call(
            api_name="web_choose_file",
            mime_type=getattr(stmt, "mime_type", "*/*"),
            tmp_prefix="web_choose_file_ignored",
        )
        return out

    def _compile_web_cookie_set_stmt(self, stmt):
        out, _ = self._compile_web_cookie_set_result_call(
            api_name="web_cookie_set",
            url=getattr(stmt, "url", ""),
            cookie=getattr(stmt, "cookie", ""),
            tmp_prefix="web_cookie_set_ignored",
        )
        return out

    def _compile_create_notification_channel_call(
        self,
        *,
        channel_id: str,
        channel_name: str,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name="create_notification_channel",
            capability_name="Notifications",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "createChannel",
                    args=[var("ctx"), const(str(channel_id)), const(str(channel_name))],
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

    def _compile_notify_result_call(
        self,
        *,
        api_name: str = "notify_result",
        title: str,
        body: str,
        channel_id: str,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name=api_name,
            capability_name="Notifications",
            require_helper_method=True,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    binding.helper_method,
                    args=[
                        var("ctx"),
                        const(str(title)),
                        const(str(body)),
                        const(str(channel_id)),
                    ],
                    return_type="I",
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

    def _compile_notify_error_call(
        self,
        *,
        title: str,
        body: str,
        channel_id: str,
        tmp_prefix: str,
    ):
        binding = self._require_helper_capability(
            api_name="notify_error",
            capability_name="Notifications",
            require_helper_method=False,
        )
        result_tmp = self._next_tmp(tmp_prefix)
        return [
            assign("ctx", static_get("app_ctx", "Landroid/app/Activity;")),
            assign(
                result_tmp,
                call(
                    "postNotificationError",
                    args=[
                        var("ctx"),
                        const(str(title)),
                        const(str(body)),
                        const(str(channel_id)),
                    ],
                    return_type="I",
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

    def _compile_create_notification_channel_stmt(self, stmt):
        out, _ = self._compile_create_notification_channel_call(
            channel_id=getattr(stmt, "channel_id", ""),
            channel_name=getattr(stmt, "channel_name", ""),
            tmp_prefix="notification_channel_ignored",
        )
        return out

    def _compile_notify_stmt(self, stmt):
        out, _ = self._compile_notify_result_call(
            api_name="notify",
            title=getattr(stmt, "title", ""),
            body=getattr(stmt, "body", ""),
            channel_id=getattr(stmt, "channel_id", "ahnali_default"),
            tmp_prefix="notify_ignored",
        )
        return out

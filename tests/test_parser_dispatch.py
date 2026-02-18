from dsl.parser_dispatch import EXPR_FN_BY_DOMAIN, STATEMENT_FN_BY_DOMAIN


def test_parser_dispatch_domains_include_capability_aliases():
    capability_stmt = STATEMENT_FN_BY_DOMAIN["capabilities"]
    capability_expr = EXPR_FN_BY_DOMAIN["capabilities"]

    assert "open_url" in capability_stmt
    assert "check_permission" in capability_stmt
    assert "request_permissions" in capability_stmt
    assert "notify" in capability_stmt
    assert "clipboard_set" in capability_stmt
    assert "share_text" in capability_stmt
    assert "share_file" in capability_stmt
    assert "work_enqueue" in capability_stmt
    assert "work_cancel" in capability_stmt
    assert "alarm_schedule" in capability_stmt
    assert "alarm_cancel" in capability_stmt
    assert "job_schedule" in capability_stmt
    assert "job_cancel" in capability_stmt
    assert "web_set_policy" in capability_stmt
    assert "web_load" in capability_stmt
    assert "web_add_js_bridge" in capability_stmt
    assert "web_choose_file" in capability_stmt
    assert "web_cookie_set" in capability_stmt
    assert "permission_granted" in capability_expr
    assert "location_enabled" in capability_expr
    assert "notify_error" in capability_expr
    assert "clipboard_get" in capability_expr
    assert "share_text_error" in capability_expr
    assert "share_file_result" in capability_expr
    assert "share_file_error" in capability_expr
    assert "open_external_result" in capability_expr
    assert "deep_link_get" in capability_expr
    assert "deep_link_error" in capability_expr
    assert "work_status" in capability_expr
    assert "work_error" in capability_expr
    assert "alarm_status" in capability_expr
    assert "alarm_error" in capability_expr
    assert "job_status" in capability_expr
    assert "job_error" in capability_expr
    assert "web_load_result" in capability_expr
    assert "web_load_error" in capability_expr
    assert "web_add_js_bridge_result" in capability_expr
    assert "web_add_js_bridge_error" in capability_expr
    assert "web_choose_file_result" in capability_expr
    assert "web_choose_file_error" in capability_expr
    assert "web_cookie_set_result" in capability_expr
    assert "web_cookie_set_error" in capability_expr
    assert "web_cookie_get" in capability_expr
    assert "web_cookie_get_error" in capability_expr


def test_parser_dispatch_domains_include_motion_aliases():
    motion = STATEMENT_FN_BY_DOMAIN["motion"]
    assert "animate" in motion
    assert "fade_in" in motion
    assert "animate_elevation" in motion


def test_parser_dispatch_domains_include_navigation_aliases():
    navigation = STATEMENT_FN_BY_DOMAIN["navigation"]
    assert "navigate" in navigation
    assert "back" in navigation
    assert "replace" in navigation
    assert "pop_to_root" in navigation
    assert "clear_stack" in navigation


def test_parser_dispatch_domains_include_hybrid_aliases():
    hybrid_stmt = STATEMENT_FN_BY_DOMAIN["hybrid"]
    hybrid_expr = EXPR_FN_BY_DOMAIN["hybrid"]
    assert "observable" in hybrid_stmt
    assert "set_observable" in hybrid_stmt
    assert "bind_text" in hybrid_stmt
    assert "observable_get" in hybrid_expr

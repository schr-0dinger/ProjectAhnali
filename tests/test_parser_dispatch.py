from dsl.parser_dispatch import EXPR_FN_BY_DOMAIN, STATEMENT_FN_BY_DOMAIN


def test_parser_dispatch_domains_include_capability_aliases():
    capability_stmt = STATEMENT_FN_BY_DOMAIN["capabilities"]
    capability_expr = EXPR_FN_BY_DOMAIN["capabilities"]

    assert "open_url" in capability_stmt
    assert "check_permission" in capability_stmt
    assert "request_permissions" in capability_stmt
    assert "permission_granted" in capability_expr
    assert "location_enabled" in capability_expr


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

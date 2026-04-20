"""Unit tests for scripts/lib/filter.py -- language detection and file filtering."""

import os

import pytest

from filter import detect_language, is_filtered, is_test_file


PROJECT_ROOT = "/tmp/myproject"


def _filtered(rel_path: str, ignore_patterns: list | None = None) -> bool:
    return is_filtered(
        os.path.join(PROJECT_ROOT, rel_path),
        PROJECT_ROOT,
        ignore_patterns or [],
    )


# ---------------------------------------------------------------------------
# detect_language
# ---------------------------------------------------------------------------


class TestDetectLanguage:
    def test_python(self):
        assert detect_language("main.py") == "python"

    def test_typescript(self):
        assert detect_language("service.ts") == "typescript"

    def test_tsx(self):
        assert detect_language("App.tsx") == "typescript"

    def test_javascript(self):
        assert detect_language("index.js") == "javascript"

    def test_jsx(self):
        assert detect_language("Button.jsx") == "javascript"

    def test_go(self):
        assert detect_language("handler.go") == "go"

    def test_ruby(self):
        assert detect_language("user.rb") == "ruby"

    def test_rust(self):
        assert detect_language("lib.rs") == "rust"

    def test_php(self):
        assert detect_language("Controller.php") == "php"

    def test_java(self):
        assert detect_language("Service.java") == "java"

    def test_unknown_returns_none(self):
        assert detect_language("data.csv") is None

    def test_case_insensitive(self):
        assert detect_language("Main.PY") == "python"

    def test_no_extension(self):
        assert detect_language("Makefile") is None


# ---------------------------------------------------------------------------
# is_test_file
# ---------------------------------------------------------------------------


class TestIsTestFile:
    def test_python_prefix(self):
        assert is_test_file("test_billing.py")

    def test_python_prefix_with_path(self):
        assert is_test_file("tests/test_billing.py")

    def test_go_suffix(self):
        assert is_test_file("handler_test.go")

    def test_js_dot_test(self):
        assert is_test_file("billing.test.ts")

    def test_js_spec(self):
        assert is_test_file("billing.spec.ts")

    def test_ruby_spec(self):
        assert is_test_file("user_spec.rb")

    def test_java_test(self):
        assert is_test_file("BillingServiceTest.java")

    def test_java_tests(self):
        assert is_test_file("BillingServiceTests.java")

    def test_java_it(self):
        assert is_test_file("BillingServiceIT.java")

    def test_not_test_file(self):
        assert not is_test_file("billing.py")

    def test_not_test_file_ts(self):
        assert not is_test_file("service.ts")


# ---------------------------------------------------------------------------
# is_filtered -- extension
# ---------------------------------------------------------------------------


class TestIsFilteredByExtension:
    def test_yaml_skipped(self):
        assert _filtered("config.yaml")

    def test_yml_skipped(self):
        assert _filtered(".github/workflows/ci.yml")

    def test_json_skipped(self):
        assert _filtered("tsconfig.json")

    def test_toml_skipped(self):
        assert _filtered("pyproject.toml")

    def test_md_skipped(self):
        assert _filtered("README.md")

    def test_html_skipped(self):
        assert _filtered("index.html")

    def test_css_skipped(self):
        assert _filtered("styles.css")

    def test_graphql_skipped(self):
        assert _filtered("schema.graphql")

    def test_dockerfile_skipped(self):
        assert _filtered("Dockerfile")

    def test_dockerfile_variant_skipped(self):
        assert _filtered("api.dockerfile")

    def test_svg_skipped(self):
        assert _filtered("logo.svg")

    def test_sql_skipped(self):
        assert _filtered("schema.sql")


# ---------------------------------------------------------------------------
# is_filtered -- path fragments
# ---------------------------------------------------------------------------


class TestIsFilteredByPath:
    def test_node_modules_skipped(self):
        assert _filtered("node_modules/lodash/index.js")

    def test_venv_skipped(self):
        assert _filtered(".venv/lib/python3.11/site-packages/requests.py")

    def test_dist_skipped(self):
        assert _filtered("dist/bundle.js")

    def test_build_skipped(self):
        assert _filtered("build/output.js")

    def test_git_skipped(self):
        assert _filtered(".git/hooks/pre-commit")

    def test_migrations_skipped(self):
        assert _filtered("migrations/0001_initial.py")

    def test_pycache_skipped(self):
        assert _filtered("app/__pycache__/billing.cpython-311.pyc")

    def test_next_dir_skipped(self):
        assert _filtered(".next/static/chunks/main.js")

    def test_cursor_state_skipped(self):
        assert _filtered(".cursor/hooks/state/tailtest.json")

    def test_cursor_dir_skipped(self):
        assert _filtered(".cursor/settings.json")


# ---------------------------------------------------------------------------
# is_filtered -- build config
# ---------------------------------------------------------------------------


class TestIsFilteredBuildConfig:
    def test_vite_config_skipped(self):
        assert _filtered("vite.config.ts")

    def test_webpack_config_skipped(self):
        assert _filtered("webpack.config.js")

    def test_tailwind_config_skipped(self):
        assert _filtered("tailwind.config.js")

    def test_next_config_skipped(self):
        assert _filtered("next.config.mjs")

    def test_regular_ts_not_skipped(self):
        assert not _filtered("services/billing.ts")


# ---------------------------------------------------------------------------
# is_filtered -- test files
# ---------------------------------------------------------------------------


class TestIsFilteredTestFiles:
    def test_python_test_skipped(self):
        assert _filtered("tests/test_billing.py")

    def test_go_test_skipped(self):
        assert _filtered("handler_test.go")

    def test_js_spec_skipped(self):
        assert _filtered("billing.spec.ts")

    def test_java_test_class_skipped(self):
        assert _filtered("BillingServiceTest.java")


# ---------------------------------------------------------------------------
# is_filtered -- boilerplate
# ---------------------------------------------------------------------------


class TestIsFilteredBoilerplate:
    def test_manage_py_skipped(self):
        assert _filtered("manage.py")

    def test_wsgi_skipped(self):
        assert _filtered("wsgi.py")

    def test_asgi_skipped(self):
        assert _filtered("asgi.py")

    def test_middleware_ts_skipped(self):
        assert _filtered("middleware.ts")

    def test_middleware_js_skipped(self):
        assert _filtered("middleware.js")


# ---------------------------------------------------------------------------
# is_filtered -- generated
# ---------------------------------------------------------------------------


class TestIsFilteredGenerated:
    def test_go_mock_skipped(self):
        assert _filtered("mock_user.go")

    def test_go_mock_suffix_skipped(self):
        assert _filtered("user_mock.go")

    def test_go_proto_skipped(self):
        assert _filtered("user.pb.go")

    def test_go_gen_skipped(self):
        assert _filtered("schema_gen.go")

    def test_ts_generated_skipped(self):
        assert _filtered("types.generated.ts")

    def test_regular_go_not_skipped(self):
        assert not _filtered("handler.go")

    def test_regular_ts_not_skipped(self):
        assert not _filtered("service.ts")


# ---------------------------------------------------------------------------
# is_filtered -- .tailtest-ignore
# ---------------------------------------------------------------------------


class TestIsFilteredTailTestIgnore:
    def test_exact_path_match(self):
        assert _filtered("scripts/seed.py", ["scripts/seed.py"])

    def test_glob_pattern(self):
        assert _filtered("scripts/seed.py", ["scripts/*.py"])

    def test_filename_glob(self):
        assert _filtered("scripts/seed.py", ["seed.py"])

    def test_no_match(self):
        assert not _filtered("scripts/seed.py", ["other/*.py"])

    def test_directory_pattern_trailing_slash(self):
        assert _filtered("scripts/deploy.py", ["scripts/"])

    def test_directory_pattern_nested(self):
        assert _filtered("scripts/nested/deploy.py", ["scripts/"])

    def test_directory_pattern_does_not_match_sibling(self):
        assert not _filtered("services/billing.py", ["scripts/"])


# ---------------------------------------------------------------------------
# is_filtered -- pass-through
# ---------------------------------------------------------------------------


class TestIsFilteredPassThrough:
    def test_python_source_passes(self):
        assert not _filtered("services/billing.py")

    def test_typescript_source_passes(self):
        assert not _filtered("src/services/billing.ts")

    def test_go_source_passes(self):
        assert not _filtered("internal/handler.go")

    def test_ruby_source_passes(self):
        assert not _filtered("app/models/user.rb")

    def test_rust_source_passes(self):
        assert not _filtered("src/lib.rs")

    def test_php_source_passes(self):
        assert not _filtered("app/Http/Controllers/UserController.php")

    def test_java_source_passes(self):
        assert not _filtered("src/main/java/BillingService.java")

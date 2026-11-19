"""Test scenarios for JSONPlaceholder /posts API."""

from __future__ import annotations

import json
import time

import pytest

REQUIRED_POST_FIELDS = ("userId", "id", "title", "body")
FIELD_TYPE_EXPECTATIONS = {
    "userId": int,
    "id": int,
    "title": str,
    "body": str,
}


@pytest.mark.positive
class TestPostsPositive:
    """Positive API scenarios for /posts."""

    # TC_01
    def test_tc_01_get_posts_returns_http_200(self, api_client) -> None:
        response = api_client.get("/posts")
        assert response.status_code == 200, (
            f"Expected HTTP 200 for GET /posts, got {response.status_code}"
        )

    # TC_02
    def test_tc_02_response_content_type_is_json(self, api_client) -> None:
        response = api_client.get("/posts")
        content_type = response.headers.get("Content-Type", "")
        assert "application/json" in content_type.lower(), (
            f"Expected JSON content type, got: {content_type!r}"
        )

    # TC_03
    def test_tc_03_response_body_is_non_empty_list(self, api_client) -> None:
        response = api_client.get("/posts")
        data = response.json()
        assert isinstance(data, list), "Response body should be a JSON array"
        assert len(data) > 0, "Posts list should not be empty"

    # TC_04
    @pytest.mark.parametrize("field_name", REQUIRED_POST_FIELDS)
    def test_tc_04_each_post_contains_required_fields(
        self, posts_list: list[dict], field_name: str
    ) -> None:
        for index, post in enumerate(posts_list):
            assert field_name in post, (
                f"Post at index {index} missing field '{field_name}'"
            )

    # TC_05
    @pytest.mark.parametrize("field_name,expected_type", list(FIELD_TYPE_EXPECTATIONS.items()))
    def test_tc_05_post_field_data_types(
        self, posts_list: list[dict], field_name: str, expected_type: type
    ) -> None:
        for index, post in enumerate(posts_list):
            value = post[field_name]
            assert isinstance(value, expected_type), (
                f"Post {index}: '{field_name}' expected {expected_type.__name__}, "
                f"got {type(value).__name__}"
            )

    # TC_06
    def test_tc_06_post_ids_are_unique(self, posts_list: list[dict]) -> None:
        ids = [post["id"] for post in posts_list]
        assert len(ids) == len(set(ids)), "Duplicate post IDs found in /posts response"

    # TC_07
    def test_tc_07_get_single_post_by_id(self, api_client) -> None:
        post_id = 1
        response = api_client.get(f"/posts/{post_id}")
        assert response.status_code == 200
        post = response.json()
        assert post["id"] == post_id, f"Expected id={post_id}, got {post['id']}"
        for field in REQUIRED_POST_FIELDS:
            assert field in post, f"Single post missing '{field}'"
        assert isinstance(post["userId"], int)
        assert isinstance(post["title"], str) and post["title"]
        assert isinstance(post["body"], str) and post["body"]

    # TC_10
    def test_tc_10_response_time_within_threshold(
        self, api_client, settings
    ) -> None:
        start = time.perf_counter()
        response = api_client.get("/posts")
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert response.status_code == 200
        assert elapsed_ms <= settings.response_time_threshold_ms, (
            f"Response time {elapsed_ms:.2f}ms exceeded threshold "
            f"{settings.response_time_threshold_ms}ms"
        )


@pytest.mark.negative
class TestPostsNegative:
    """Negative API scenarios for /posts."""

    # TC_08 — JSONPlaceholder returns 404 with body {}
    def test_tc_08_get_nonexistent_post_returns_404_empty_json(self, api_client) -> None:
        response = api_client.get("/posts/9999")
        assert response.status_code == 404, (
            f"Expected 404 for GET /posts/9999, got {response.status_code}"
        )
        assert response.json() == {}, (
            "JSONPlaceholder returns an empty JSON object for missing posts"
        )

    # TC_09
    @pytest.mark.parametrize(
        "invalid_path",
        [
            "/posts/not-a-number",
            "/invalid/posts",
        ],
        ids=["non_numeric_id", "invalid_resource_path"],
    )
    def test_tc_09_invalid_path_returns_404(self, api_client, invalid_path: str) -> None:
        response = api_client.get(invalid_path)
        assert response.status_code == 404, (
            f"Expected 404 for GET {invalid_path}, got {response.status_code}"
        )
        # Observed behavior: 404 with empty JSON object for these paths
        try:
            body = response.json()
        except json.JSONDecodeError:
            pytest.fail(f"Expected JSON body for 404 on {invalid_path}")
        assert body == {}, f"Expected empty JSON object, got {body!r}"
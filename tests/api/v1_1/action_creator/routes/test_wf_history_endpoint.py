from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from starlette import status

from src.api.v1_1.action_creator.schemas import (
    DEFAULT_PAGE_IDX,
    ActionCreatorJobSummary,
    OrderDirection,
    PaginationResults,
)
from src.services.ades.fake_client import GET_JOB_LIST_RESPONSE
from src.services.ades.schemas import JobList, JobType, StatusCode

if TYPE_CHECKING:
    from starlette.testclient import TestClient

TOTAL_ITEMS = len(GET_JOB_LIST_RESPONSE["jobs"])  # type: ignore[arg-type]


def test_get_job_submissions_endpoint_returns_valid_response_no_params(
    client: TestClient,
    mocked_ades_factory: MagicMock,  # noqa: ARG001
    auth_token_module_scoped: str,
) -> None:
    # Act
    response = client.get(
        "/api/v1.1/action-creator/submissions", headers={"Authorization": f"Bearer {auth_token_module_scoped}"}
    )

    # Assert
    pagination_results = PaginationResults[ActionCreatorJobSummary](**response.json())
    assert response.status_code == status.HTTP_200_OK
    assert pagination_results.total_items == TOTAL_ITEMS
    assert pagination_results.current_page == DEFAULT_PAGE_IDX
    assert pagination_results.results_on_current_page == GET_JOB_LIST_RESPONSE["numberTotal"]
    assert pagination_results.ordered_by == "submitted_at"
    assert pagination_results.order_direction == OrderDirection.asc
    assert pagination_results.total_pages == 1
    assert len(pagination_results.results) == GET_JOB_LIST_RESPONSE["numberTotal"]
    for i in range(len(pagination_results.results) - 1):
        assert pagination_results.results[i].submitted_at <= pagination_results.results[i + 1].submitted_at


@patch("src.api.v1_1.action_creator.routes.ades_client_factory")
def test_get_job_submissions_returns_empty_result_set_when_ades_job_history_is_empty(
    ades_factory_mock: MagicMock,
    client: TestClient,
    auth_token_module_scoped: str,
) -> None:
    # Arrange
    ades_mock = MagicMock()
    list_jobs_mock = AsyncMock(return_value=(None, JobList(jobs=[], links=[], numberTotal=0).model_dump(mode="json")))
    ades_mock.list_job_submissions = list_jobs_mock
    ades_factory_mock.return_value = ades_mock

    # Act
    response = client.get(
        "/api/v1.1/action-creator/submissions", headers={"Authorization": f"Bearer {auth_token_module_scoped}"}
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    pagination_results = PaginationResults[ActionCreatorJobSummary](**response.json())
    assert pagination_results.total_items == 0
    assert pagination_results.current_page == DEFAULT_PAGE_IDX
    assert pagination_results.results_on_current_page == 0
    assert pagination_results.ordered_by == "submitted_at"
    assert pagination_results.order_direction == OrderDirection.asc
    assert pagination_results.total_pages == 0
    assert len(pagination_results.results) == 0


@patch("src.api.v1_1.action_creator.routes.ades_client_factory")
def test_get_job_submissions_returns_correct_pagination_with_fewer_jobs_than_per_page(
    ades_factory_mock: MagicMock,
    client: TestClient,
    auth_token_module_scoped: str,
) -> None:
    # Arrange
    num_jobs = 10
    jobs = [
        {
            "jobID": f"job-{i}",
            "processID": f"process-{i}",
            "status": StatusCode.successful,
            "created": datetime.now(tz=timezone.utc),
            "finished": datetime.now(tz=timezone.utc),
            "type": JobType.process,
            "links": [],
        }
        for i in range(num_jobs)
    ]

    fake_ades_client = MagicMock()
    fake_ades_client.list_job_submissions = AsyncMock(
        return_value=(None, {"jobs": jobs, "numberTotal": num_jobs, "links": []})
    )
    ades_factory_mock.return_value = fake_ades_client

    # Act
    response = client.get(
        "/api/v1.1/action-creator/submissions", headers={"Authorization": f"Bearer {auth_token_module_scoped}"}
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    pagination_results = PaginationResults[ActionCreatorJobSummary](**response.json())
    assert pagination_results.total_items == num_jobs
    assert pagination_results.total_pages == 1
    assert pagination_results.current_page == DEFAULT_PAGE_IDX
    assert pagination_results.results_on_current_page == num_jobs
    assert len(pagination_results.results) == num_jobs
    assert pagination_results.ordered_by == "submitted_at"
    assert pagination_results.order_direction == OrderDirection.asc
    for i in range(len(pagination_results.results) - 1):
        assert pagination_results.results[i].submitted_at <= pagination_results.results[i + 1].submitted_at


@pytest.mark.parametrize(
    "order_direction",
    ["asc", "desc"],
)
@pytest.mark.parametrize(
    "order_by",
    ["submission_id", "status", "function_identifier", "submitted_at", "finished_at", "successful"],
)
def test_get_job_submissions_sorts_results_by_order_by_and_direction(
    mocked_ades_factory: MagicMock,  # noqa: ARG001
    client: TestClient,
    auth_token_module_scoped: str,
    order_by: str,
    order_direction: str,
) -> None:
    # Act
    response = client.get(
        "/api/v1.1/action-creator/submissions",
        headers={"Authorization": f"Bearer {auth_token_module_scoped}"},
        params={
            "order_by": order_by,
            "order_direction": order_direction,
        },
    )

    # Assert
    pagination_results = PaginationResults[ActionCreatorJobSummary](**response.json())
    items = response.json()["results"]
    assert response.status_code == status.HTTP_200_OK
    assert pagination_results.total_items == TOTAL_ITEMS
    assert pagination_results.current_page == DEFAULT_PAGE_IDX
    assert pagination_results.results_on_current_page == GET_JOB_LIST_RESPONSE["numberTotal"]
    assert pagination_results.ordered_by == order_by
    assert pagination_results.order_direction == order_direction
    assert pagination_results.total_pages == 1
    assert len(pagination_results.results) == GET_JOB_LIST_RESPONSE["numberTotal"]
    for i in range(len(pagination_results.results) - 1):
        # Use tuples to handle None items - tuples are sorted item by item
        first = items[i][order_by]
        second = items[i + 1][order_by]

        first_tuple = (first is None, first)
        second_tuple = (second is None, second)

        if order_direction == "asc":
            assert first_tuple <= second_tuple
        else:
            assert first_tuple >= second_tuple


@pytest.mark.parametrize("page", [1, 2, 3, 4, 5], ids=lambda x: f"page={x}")
@pytest.mark.parametrize("per_page", [1, 15, 30, 50, 80, 100], ids=lambda x: f"per_page={x}")
def test_get_job_submissions_with_custom_per_page_item_count_and_page_idx(
    mocked_ades_factory: MagicMock,  # noqa: ARG001
    client: TestClient,
    auth_token_module_scoped: str,
    page: int,
    per_page: int,
) -> None:
    headers = {"Authorization": f"Bearer {auth_token_module_scoped}"}
    params = {"page": page, "per_page": per_page}

    # Act
    response = client.get("/api/v1.1/action-creator/submissions", headers=headers, params=params)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    expected_pages = math.ceil(TOTAL_ITEMS / per_page)
    pagination_results = PaginationResults[ActionCreatorJobSummary](**response.json())
    assert pagination_results.total_items == TOTAL_ITEMS
    assert pagination_results.total_pages == expected_pages
    assert pagination_results.current_page == page
    assert len(pagination_results.results) == pagination_results.results_on_current_page

    if per_page >= TOTAL_ITEMS and page < expected_pages:
        assert pagination_results.results_on_current_page == TOTAL_ITEMS
    elif per_page <= TOTAL_ITEMS and page < expected_pages:
        assert pagination_results.results_on_current_page == per_page
    elif per_page >= TOTAL_ITEMS and page == expected_pages:
        assert pagination_results.results_on_current_page == TOTAL_ITEMS
    elif per_page <= TOTAL_ITEMS and page == expected_pages:
        assert pagination_results.results_on_current_page <= per_page
    else:
        assert pagination_results.results_on_current_page == 0
        assert len(pagination_results.results) == 0

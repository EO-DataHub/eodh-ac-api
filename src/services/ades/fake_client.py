from __future__ import annotations

from typing import TYPE_CHECKING, Any

from starlette import status

from src.services.ades.base_client import ADESClientBase, ErrorResponse
from src.services.ades.schemas import JobList, Process, ProcessList, ProcessSummary, StatusInfo

if TYPE_CHECKING:
    from pathlib import Path
    from uuid import UUID


GET_PROCESS_LIST_RESPONSE = {
    "processes": [
        {
            "id": "display",
            "title": "Print Cheetah templates as HTML",
            "description": "Print Cheetah templates as HTML.",
            "mutable": False,
            "version": "2.0.0",
            "jobControlOptions": ["sync-execute", "async-execute", "dismiss"],
            "outputTransmission": ["value", "reference"],
            "links": [
                {
                    "rel": "self",
                    "type": "application/json",
                    "title": "Process Description",
                    "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/processes/display",
                }
            ],
        },
        {
            "id": "echo",
            "title": "Echo input",
            "description": "Simply echo the value provided as input",
            "mutable": False,
            "version": "2.0.0",
            "metadata": [{"title": "Demo"}],
            "jobControlOptions": ["sync-execute", "async-execute", "dismiss"],
            "outputTransmission": ["value", "reference"],
            "links": [
                {
                    "rel": "self",
                    "type": "application/json",
                    "title": "Process Description",
                    "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/processes/echo",
                }
            ],
        },
    ],
    "links": [
        {
            "rel": "self",
            "type": "application/json",
            "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/processes",
        }
    ],
}
REGISTER_PROCESS_RESPONSE = {
    "id": "raster-calculate",
    "title": "Test raster calculator for Spyrosoft workflows",
    "description": "Test raster calculator for Spyrosoft workflows",
    "mutable": True,
    "version": "0.1.2",
    "metadata": [{"role": "https://schema.org/softwareVersion", "value": "0.1.2"}],
    "outputTransmission": ["value", "reference"],
    "jobControlOptions": ["async-execute", "dismiss"],
    "links": [
        {
            "rel": "http://www.opengis.net/def/rel/ogc/1.0/execute",
            "type": "application/json",
            "title": "Execute End Point",
            "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/processes/raster-calculate/execution",
        }
    ],
}
GET_PROCESS_DETAILS_RESPONSE = {
    "id": "raster-calculate",
    "title": "Test raster calculator for Spyrosoft workflows",
    "description": "Test raster calculator for Spyrosoft workflows",
    "mutable": True,
    "version": "0.1.2",
    "metadata": [{"role": "https://schema.org/softwareVersion", "value": "0.1.2"}],
    "outputTransmission": ["value", "reference"],
    "jobControlOptions": ["async-execute", "dismiss"],
    "links": [
        {
            "rel": "http://www.opengis.net/def/rel/ogc/1.0/execute",
            "type": "application/json",
            "title": "Execute End Point",
            "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/processes/raster-calculate/execution",
        }
    ],
    "inputs": {
        "aoi": {
            "title": "lorem ipsum dolor sit amet",
            "description": "lorem ipsum dolor sit amet",
            "schema": {"type": "string", "nullable": True},
        },
        "date_end": {
            "title": "lorem ipsum dolor sit amet",
            "description": "lorem ipsum dolor sit amet",
            "schema": {"type": "string", "nullable": True},
        },
        "date_start": {
            "title": "lorem ipsum dolor sit amet",
            "description": "lorem ipsum dolor sit amet",
            "schema": {"type": "string", "nullable": True},
        },
        "index": {
            "title": "lorem ipsum dolor sit amet",
            "description": "lorem ipsum dolor sit amet",
            "schema": {"type": "string", "nullable": True},
        },
        "stac_collection": {
            "title": "stac collection to use",
            "description": "stac collection to use",
            "schema": {"type": "string", "nullable": True},
        },
    },
    "outputs": {
        "results": {
            "title": "results",
            "description": "None",
            "extended-schema": {
                "oneOf": [
                    {
                        "allOf": [
                            {"$ref": "http://zoo-project.org/dl/link.json"},
                            {"type": "object", "properties": {"type": {"enum": ["application/json"]}}},
                        ]
                    },
                    {"type": "object", "required": ["value"], "properties": {"value": {"oneOf": [{"type": "object"}]}}},
                ]
            },
            "schema": {"oneOf": [{"type": "object"}]},
        }
    },
}
EXECUTE_PROCESS_RESPONSE = {
    "jobID": "e5378640-8325-11ef-8d25-9625a5233070",
    "type": "process",
    "processID": "raster-calculate",
    "created": "2024-10-05T14:27:05.752Z",
    "started": "2024-10-05T14:27:05.752Z",
    "updated": "2024-10-05T14:27:05.752Z",
    "status": "running",
    "message": "ZOO-Kernel accepted to run your service!",
    "links": [
        {
            "title": "Status location",
            "rel": "monitor",
            "type": "application/json",
            "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/e5378640-8325-11ef-8d25-9625a5233070",
        }
    ],
}
GET_JOB_IN_PROGRESS_STATUS_RESPONSE = {
    "progress": 15,
    "jobID": "e5378640-8325-11ef-8d25-9625a5233070",
    "type": "process",
    "processID": "raster-calculate",
    "created": "2024-10-05T14:27:05.752Z",
    "started": "2024-10-05T14:27:05.752Z",
    "updated": "2024-10-05T14:27:32.367Z",
    "status": "running",
    "message": "processing environment created, preparing execution",
    "links": [
        {
            "title": "Status location",
            "rel": "monitor",
            "type": "application/json",
            "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/e5378640-8325-11ef-8d25-9625a5233070",
        }
    ],
}
GET_JOB_FINISHED_STATUS_RESPONSE = {
    "jobID": "e5378640-8325-11ef-8d25-9625a5233070",
    "type": "process",
    "processID": "raster-calculate",
    "created": "2024-10-05T14:27:05.752Z",
    "started": "2024-10-05T14:27:05.752Z",
    "finished": "2024-10-05T14:35:01.369Z",
    "updated": "2024-10-05T14:35:01.057Z",
    "status": "successful",
    "message": "ZOO-Kernel successfully run your service!",
    "links": [
        {
            "title": "Status location",
            "rel": "monitor",
            "type": "application/json",
            "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/e5378640-8325-11ef-8d25-9625a5233070",
        },
        {
            "title": "Result location",
            "rel": "http://www.opengis.net/def/rel/ogc/1.0/results",
            "type": "application/json",
            "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/e5378640-8325-11ef-8d25-9625a5233070/results",
        },
        {
            "href": "https://test.eodatahub.org.uk/ades/temp/raster-calculate-e5378640-8325-11ef-8d25-9625a5233070/calculator.log",
            "title": "Tool log calculator.log",
            "rel": "related",
            "type": "text/plain",
        },
        {
            "href": "https://test.eodatahub.org.uk/ades/temp/raster-calculate-e5378640-8325-11ef-8d25-9625a5233070/node_stage_out.log",
            "title": "Tool log node_stage_out.log",
            "rel": "related",
            "type": "text/plain",
        },
    ],
}
GET_JOB_LIST_RESPONSE = {
    "jobs": [
        {
            "progress": 20,
            "jobID": "e5378640-8325-11ef-8d25-9625a5233070",
            "type": "process",
            "processID": "raster-calculate",
            "created": "2024-10-05T14:27:05.752Z",
            "started": "2024-10-05T14:27:05.752Z",
            "updated": "2024-10-05T14:27:47.602Z",
            "status": "running",
            "message": "execution submitted",
            "links": [
                {
                    "title": "Status location",
                    "rel": "monitor",
                    "type": "application/json",
                    "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/e5378640-8325-11ef-8d25-9625a5233070",
                }
            ],
        }
    ],
    "links": [
        {
            "rel": "self",
            "type": "application/json",
            "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs",
        }
    ],
    "numberTotal": 1,
}
GET_JOB_RESULTS_RESPONSE = {
    "type": "Collection",
    "id": "e5378640-8325-11ef-8d25-9625a5233070",
    "stac_version": "1.0.0",
    "description": "description",
    "links": [
        {
            "rel": "root",
            "href": "s3://eodhp-test-workspaces1/eopro-spyro-test/processing-results/cat_e5378640-8325-11ef-8d25-9625a5233070.json",
            "type": "application/json",
        },
        {
            "rel": "item",
            "href": "s3://eodhp-test-workspaces1/eopro-spyro-test/processing-results/cat_e5378640-8325-11ef-8d25-9625a5233070/col_e5378640-8325-11ef-8d25-9625a5233070/S2A_MSIL2A_20241004T100851_R022_T33UWS_20241004T144252-1728138785.0044188.json",
            "type": "application/json",
        },
        {
            "rel": "item",
            "href": "s3://eodhp-test-workspaces1/eopro-spyro-test/processing-results/cat_e5378640-8325-11ef-8d25-9625a5233070/col_e5378640-8325-11ef-8d25-9625a5233070/S2A_MSIL2A_20241004T100851_R022_T33UVS_20241004T144252-1728138792.325989.json",
            "type": "application/json",
        },
        {
            "rel": "item",
            "href": "s3://eodhp-test-workspaces1/eopro-spyro-test/processing-results/cat_e5378640-8325-11ef-8d25-9625a5233070/col_e5378640-8325-11ef-8d25-9625a5233070/S2A_MSIL2A_20241001T100031_R122_T33UWS_20241001T123351-1728138799.7334049.json",
            "type": "application/json",
        },
        {
            "rel": "item",
            "href": "s3://eodhp-test-workspaces1/eopro-spyro-test/processing-results/cat_e5378640-8325-11ef-8d25-9625a5233070/col_e5378640-8325-11ef-8d25-9625a5233070/S2A_MSIL2A_20241001T100031_R122_T33UVS_20241001T123351-1728138808.406498.json",
            "type": "application/json",
        },
        {
            "rel": "item",
            "href": "s3://eodhp-test-workspaces1/eopro-spyro-test/processing-results/cat_e5378640-8325-11ef-8d25-9625a5233070/col_e5378640-8325-11ef-8d25-9625a5233070/S2B_MSIL2A_20240929T100719_R022_T33UWS_20240929T133706-1728138815.1905165.json",
            "type": "application/json",
        },
        {
            "rel": "item",
            "href": "s3://eodhp-test-workspaces1/eopro-spyro-test/processing-results/cat_e5378640-8325-11ef-8d25-9625a5233070/col_e5378640-8325-11ef-8d25-9625a5233070/S2B_MSIL2A_20240929T100719_R022_T33UVS_20240929T133706-1728138823.0220628.json",
            "type": "application/json",
        },
        {
            "rel": "item",
            "href": "s3://eodhp-test-workspaces1/eopro-spyro-test/processing-results/cat_e5378640-8325-11ef-8d25-9625a5233070/col_e5378640-8325-11ef-8d25-9625a5233070/S2B_MSIL2A_20240926T100029_R122_T33UWS_20240926T123056-1728138829.6239152.json",
            "type": "application/json",
        },
        {
            "rel": "item",
            "href": "s3://eodhp-test-workspaces1/eopro-spyro-test/processing-results/cat_e5378640-8325-11ef-8d25-9625a5233070/col_e5378640-8325-11ef-8d25-9625a5233070/S2B_MSIL2A_20240926T100029_R122_T33UVS_20240926T123056-1728138837.602131.json",
            "type": "application/json",
        },
        {
            "rel": "item",
            "href": "s3://eodhp-test-workspaces1/eopro-spyro-test/processing-results/cat_e5378640-8325-11ef-8d25-9625a5233070/col_e5378640-8325-11ef-8d25-9625a5233070/S2A_MSIL2A_20240924T100741_R022_T33UWS_20240924T143752-1728138843.6100957.json",
            "type": "application/json",
        },
        {
            "rel": "item",
            "href": "s3://eodhp-test-workspaces1/eopro-spyro-test/processing-results/cat_e5378640-8325-11ef-8d25-9625a5233070/col_e5378640-8325-11ef-8d25-9625a5233070/S2A_MSIL2A_20240924T100741_R022_T33UVS_20240924T143752-1728138850.4540675.json",
            "type": "application/json",
        },
        {
            "rel": "self",
            "href": "s3://eodhp-test-workspaces1/eopro-spyro-test/processing-results/cat_e5378640-8325-11ef-8d25-9625a5233070/collection.json",
            "type": "application/json",
        },
        {
            "rel": "parent",
            "href": "s3://eodhp-test-workspaces1/eopro-spyro-test/processing-results/cat_e5378640-8325-11ef-8d25-9625a5233070.json",
            "type": "application/json",
        },
    ],
    "title": "Result Collection",
    "extent": {
        "spatial": {"bbox": [[-180, -90, 180, 90]]},
        "temporal": {"interval": [["2024-10-05T14:33:05.004419Z", "2024-10-05T14:34:10.454067Z"]]},
    },
    "license": "proprietary",
    "keywords": ["eoepca"],
}


class FakeADESClient(ADESClientBase):
    async def get_job_details(self, job_id: str | UUID) -> tuple[ErrorResponse | None, StatusInfo | None]:
        return None, StatusInfo(**GET_JOB_FINISHED_STATUS_RESPONSE)

    async def get_job_results(self, job_id: str | UUID) -> tuple[ErrorResponse | None, dict[str, Any] | None]:
        return None, GET_JOB_RESULTS_RESPONSE

    async def list_job_submissions(self) -> tuple[ErrorResponse | None, JobList | None]:
        return None, JobList(**GET_JOB_LIST_RESPONSE)

    async def cancel_job(self, job_id: str | UUID) -> ErrorResponse | None:
        return ErrorResponse(code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")

    async def register_process_from_cwl_href(self, cwl_href: str) -> tuple[ErrorResponse | None, ProcessSummary | None]:
        return None, ProcessSummary(**REGISTER_PROCESS_RESPONSE)

    async def register_process_from_local_cwl_file(
        self,
        cwl_location: Path,
    ) -> tuple[ErrorResponse | None, ProcessSummary | None]:
        return None, ProcessSummary(**REGISTER_PROCESS_RESPONSE)

    async def process_exists(self, process_identifier: str) -> tuple[ErrorResponse | None, bool | None]:
        return None, True

    async def ensure_process_exists(self, process_identifier: str) -> ErrorResponse | None:
        return None

    async def list_processes(self) -> tuple[ErrorResponse | None, ProcessList | None]:
        return None, ProcessList(**GET_PROCESS_LIST_RESPONSE)

    async def get_process_details(self, process_identifier: str) -> tuple[ErrorResponse | None, Process | None]:
        return None, Process(**GET_PROCESS_DETAILS_RESPONSE)

    async def execute_process(
        self,
        process_identifier: str,
        process_inputs: dict[str, Any],
    ) -> tuple[ErrorResponse | None, StatusInfo | None]:
        return None, StatusInfo(**EXECUTE_PROCESS_RESPONSE)

    async def unregister_process(self, process_identifier: str) -> ErrorResponse | None:
        return None

    async def reregister_process(self, process_identifier: str) -> tuple[ErrorResponse | None, ProcessSummary | None]:
        return None, ProcessSummary(**REGISTER_PROCESS_RESPONSE)

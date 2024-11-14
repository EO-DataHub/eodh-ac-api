from __future__ import annotations

from typing import TYPE_CHECKING, Any

from src.services.ades.base_client import ADESClientBase, ErrorResponse
from src.services.ades.schemas import JobList, Process, ProcessList, ProcessSummary, StatusCode, StatusInfo

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
GET_ALL_FAILED_JOBS_RESPONSE = [
    {
        "jobID": "cde40b3a-8479-11ef-a1a3-9625a5233070",
        "type": "process",
        "processID": "raster-calculate",
        "created": "2024-10-07T07:00:15.482Z",
        "started": "2024-10-07T07:00:15.482Z",
        "finished": "2024-10-07T07:03:06.806Z",
        "updated": "2024-10-07T07:03:02.876Z",
        "status": "failed",
        "message": 'Unable to run the Service. The message returned back by the Service was the following: Exception during execution...\nTraceback (most recent call last):\n  File "/opt/zooservices_user/eopro_spyro_test/raster-calculate/service.py", line 477, in raster_calculate\n    exit_status = runner.execute()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/zoo_calrissian_runner/__init__.py", line 451, in execute\n    output = execution.get_output()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/pycalrissian/execution.py", line 84, in get_output\n    return json.load(staged_file)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 293, in load\n    return loads(fp.read(),\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 346, in loads\n    return _default_decoder.decode(s)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 337, in decode\n    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 355, in raw_decode\n    raise JSONDecodeError("Expecting value", s, err.value) from None\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n\n',
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/cde40b3a-8479-11ef-a1a3-9625a5233070",
            }
        ],
    },
    {
        "jobID": "8c498984-847e-11ef-9912-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-07T07:34:12.894Z",
        "started": "2024-10-07T07:34:12.894Z",
        "finished": "2024-10-07T07:37:03.777Z",
        "updated": "2024-10-07T07:36:59.997Z",
        "status": "failed",
        "message": 'Unable to run the Service. The message returned back by the Service was the following: Exception during execution...\nTraceback (most recent call last):\n  File "/opt/zooservices_user/eopro_spyro_test/water_bodies/service.py", line 477, in water_bodies\n    exit_status = runner.execute()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/zoo_calrissian_runner/__init__.py", line 451, in execute\n    output = execution.get_output()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/pycalrissian/execution.py", line 84, in get_output\n    return json.load(staged_file)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 293, in load\n    return loads(fp.read(),\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 346, in loads\n    return _default_decoder.decode(s)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 337, in decode\n    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 355, in raw_decode\n    raise JSONDecodeError("Expecting value", s, err.value) from None\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n\n',
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/8c498984-847e-11ef-9912-9625a5233070",
            }
        ],
    },
    {
        "jobID": "fbe9e590-847e-11ef-8d6c-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-07T07:37:20.158Z",
        "started": "2024-10-07T07:37:20.158Z",
        "finished": "2024-10-07T07:37:20.538Z",
        "updated": "2024-10-07T07:37:20.332Z",
        "status": "failed",
        "message": "ZOO-Kernel accepted to run your service!",
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/fbe9e590-847e-11ef-8d6c-9625a5233070",
            }
        ],
    },
    {
        "jobID": "ac8d0a42-8481-11ef-928a-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-07T07:56:35.491Z",
        "started": "2024-10-07T07:56:35.491Z",
        "finished": "2024-10-07T07:59:26.352Z",
        "updated": "2024-10-07T07:59:22.774Z",
        "status": "failed",
        "message": 'Unable to run the Service. The message returned back by the Service was the following: Exception during execution...\nTraceback (most recent call last):\n  File "/opt/zooservices_user/eopro_spyro_test/water_bodies/service.py", line 477, in water_bodies\n    exit_status = runner.execute()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/zoo_calrissian_runner/__init__.py", line 451, in execute\n    output = execution.get_output()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/pycalrissian/execution.py", line 84, in get_output\n    return json.load(staged_file)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 293, in load\n    return loads(fp.read(),\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 346, in loads\n    return _default_decoder.decode(s)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 337, in decode\n    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 355, in raw_decode\n    raise JSONDecodeError("Expecting value", s, err.value) from None\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n\n',
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/ac8d0a42-8481-11ef-928a-9625a5233070",
            }
        ],
    },
    {
        "jobID": "c96d16ba-8310-11ef-b078-9625a5233070",
        "type": "process",
        "processID": "raster-calculate",
        "created": "2024-10-05T11:55:59.721Z",
        "started": "2024-10-05T11:55:59.721Z",
        "finished": "2024-10-05T11:58:49.804Z",
        "updated": "2024-10-05T11:58:47.087Z",
        "status": "failed",
        "message": 'Unable to run the Service. The message returned back by the Service was the following: Exception during execution...\nTraceback (most recent call last):\n  File "/opt/zooservices_user/eopro_spyro_test/raster-calculate/service.py", line 477, in raster_calculate\n    exit_status = runner.execute()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/zoo_calrissian_runner/__init__.py", line 451, in execute\n    output = execution.get_output()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/pycalrissian/execution.py", line 84, in get_output\n    return json.load(staged_file)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 293, in load\n    return loads(fp.read(),\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 346, in loads\n    return _default_decoder.decode(s)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 337, in decode\n    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 355, in raw_decode\n    raise JSONDecodeError("Expecting value", s, err.value) from None\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n\n',
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/c96d16ba-8310-11ef-b078-9625a5233070",
            }
        ],
    },
    {
        "jobID": "04fbf04e-818f-11ef-aa2f-9625a5233070",
        "type": "process",
        "processID": "raster-calculate",
        "created": "2024-10-03T13:54:33.894Z",
        "started": "2024-10-03T13:54:33.894Z",
        "finished": "2024-10-03T13:54:34.365Z",
        "updated": "2024-10-03T13:54:34.119Z",
        "status": "failed",
        "message": "ZOO-Kernel accepted to run your service!",
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/04fbf04e-818f-11ef-aa2f-9625a5233070",
            }
        ],
    },
    {
        "jobID": "f58e54ba-847e-11ef-8f02-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-07T07:37:09.485Z",
        "started": "2024-10-07T07:37:09.485Z",
        "finished": "2024-10-07T07:39:59.360Z",
        "updated": "2024-10-07T07:39:56.673Z",
        "status": "failed",
        "message": 'Unable to run the Service. The message returned back by the Service was the following: Exception during execution...\nTraceback (most recent call last):\n  File "/opt/zooservices_user/eopro_spyro_test/water_bodies/service.py", line 477, in water_bodies\n    exit_status = runner.execute()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/zoo_calrissian_runner/__init__.py", line 451, in execute\n    output = execution.get_output()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/pycalrissian/execution.py", line 84, in get_output\n    return json.load(staged_file)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 293, in load\n    return loads(fp.read(),\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 346, in loads\n    return _default_decoder.decode(s)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 337, in decode\n    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 355, in raw_decode\n    raise JSONDecodeError("Expecting value", s, err.value) from None\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n\n',
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/f58e54ba-847e-11ef-8f02-9625a5233070",
            }
        ],
    },
    {
        "jobID": "34d14024-847a-11ef-ac04-9625a5233070",
        "type": "process",
        "processID": "raster-calculate",
        "created": "2024-10-07T07:03:08.099Z",
        "started": "2024-10-07T07:03:08.099Z",
        "finished": "2024-10-07T07:05:58.843Z",
        "updated": "2024-10-07T07:05:55.183Z",
        "status": "failed",
        "message": 'Unable to run the Service. The message returned back by the Service was the following: Exception during execution...\nTraceback (most recent call last):\n  File "/opt/zooservices_user/eopro_spyro_test/raster-calculate/service.py", line 477, in raster_calculate\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/zoo_calrissian_runner/__init__.py", line 451, in execute\n    output = execution.get_output()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/pycalrissian/execution.py", line 84, in get_output\n    return json.load(staged_file)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 293, in load\n    return loads(fp.read(),\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 346, in loads\n    return _default_decoder.decode(s)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 337, in decode\n    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 355, in raw_decode\n    raise JSONDecodeError("Expecting value", s, err.value) from None\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n\n',
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/34d14024-847a-11ef-ac04-9625a5233070",
            }
        ],
    },
    {
        "jobID": "1b9bd36e-8482-11ef-a34d-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-07T07:59:41.901Z",
        "started": "2024-10-07T07:59:41.901Z",
        "finished": "2024-10-07T07:59:42.332Z",
        "updated": "2024-10-07T07:59:42.119Z",
        "status": "failed",
        "message": "ZOO-Kernel accepted to run your service!",
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/1b9bd36e-8482-11ef-a34d-9625a5233070",
            }
        ],
    },
    {
        "jobID": "9e2bf6f4-8312-11ef-92df-9625a5233070",
        "type": "process",
        "processID": "raster-calculate",
        "created": "2024-10-05T12:09:06.166Z",
        "started": "2024-10-05T12:09:06.166Z",
        "finished": "2024-10-05T12:11:55.766Z",
        "updated": "2024-10-05T12:11:53.143Z",
        "status": "failed",
        "message": 'Unable to run the Service. The message returned back by the Service was the following: Exception during execution...\nTraceback (most recent call last):\n  File "/opt/zooservices_user/eopro_spyro_test/raster-calculate/service.py", line 477, in raster_calculate\n    exit_status = runner.execute()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/zoo_calrissian_runner/__init__.py", line 451, in execute\n    output = execution.get_output()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/pycalrissian/execution.py", line 84, in get_output\n    return json.load(staged_file)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 293, in load\n    return loads(fp.read(),\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 346, in loads\n    return _default_decoder.decode(s)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 337, in decode\n    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 355, in raw_decode\n    raise JSONDecodeError("Expecting value", s, err.value) from None\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n\n',
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/9e2bf6f4-8312-11ef-92df-9625a5233070",
            }
        ],
    },
    {
        "jobID": "1659f430-8482-11ef-93f4-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-07T07:59:32.974Z",
        "started": "2024-10-07T07:59:32.974Z",
        "finished": "2024-10-07T08:02:23.542Z",
        "updated": "2024-10-07T08:02:19.945Z",
        "status": "failed",
        "message": 'Unable to run the Service. The message returned back by the Service was the following: Exception during execution...\nTraceback (most recent call last):\n  File "/opt/zooservices_user/eopro_spyro_test/water_bodies/service.py", line 477, in water_bodies\n    exit_status = runner.execute()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/zoo_calrissian_runner/__init__.py", line 451, in execute\n    output = execution.get_output()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/pycalrissian/execution.py", line 84, in get_output\n    return json.load(staged_file)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 293, in load\n    return loads(fp.read(),\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 346, in loads\n    return _default_decoder.decode(s)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 337, in decode\n    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 355, in raw_decode\n    raise JSONDecodeError("Expecting value", s, err.value) from None\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n\n',
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/1659f430-8482-11ef-93f4-9625a5233070",
            }
        ],
    },
    {
        "jobID": "1d1a09d6-8482-11ef-85e2-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-07T07:59:44.321Z",
        "started": "2024-10-07T07:59:44.321Z",
        "finished": "2024-10-07T08:02:34.969Z",
        "updated": "2024-10-07T08:02:31.360Z",
        "status": "failed",
        "message": 'Unable to run the Service. The message returned back by the Service was the following: Exception during execution...\nTraceback (most recent call last):\n  File "/opt/zooservices_user/eopro_spyro_test/water_bodies/service.py", line 477, in water_bodies\n    exit_status = runner.execute()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/zoo_calrissian_runner/__init__.py", line 451, in execute\n    output = execution.get_output()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/pycalrissian/execution.py", line 84, in get_output\n    return json.load(staged_file)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 293, in load\n    return loads(fp.read(),\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 346, in loads\n    return _default_decoder.decode(s)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 337, in decode\n    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 355, in raw_decode\n    raise JSONDecodeError("Expecting value", s, err.value) from None\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n\n',
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/1d1a09d6-8482-11ef-85e2-9625a5233070",
            }
        ],
    },
    {
        "jobID": "faca8c0a-847e-11ef-a22e-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-07T07:37:18.276Z",
        "started": "2024-10-07T07:37:18.276Z",
        "finished": "2024-10-07T07:37:18.592Z",
        "updated": "2024-10-07T07:37:18.406Z",
        "status": "failed",
        "message": "ZOO-Kernel accepted to run your service!",
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/faca8c0a-847e-11ef-a22e-9625a5233070",
            }
        ],
    },
    {
        "jobID": "c3ee0732-8494-11ef-951b-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-07T10:13:15.144Z",
        "started": "2024-10-07T10:13:15.144Z",
        "finished": "2024-10-07T10:16:06.081Z",
        "updated": "2024-10-07T10:16:02.399Z",
        "status": "failed",
        "message": 'Unable to run the Service. The message returned back by the Service was the following: Exception during execution...\nTraceback (most recent call last):\n  File "/opt/zooservices_user/eopro_spyro_test/water_bodies/service.py", line 477, in water_bodies\n    exit_status = runner.execute()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/zoo_calrissian_runner/__init__.py", line 451, in execute\n    output = execution.get_output()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/pycalrissian/execution.py", line 84, in get_output\n    return json.load(staged_file)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 293, in load\n    return loads(fp.read(),\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 346, in loads\n    return _default_decoder.decode(s)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 337, in decode\n    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 355, in raw_decode\n    raise JSONDecodeError("Expecting value", s, err.value) from None\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n\n',
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/c3ee0732-8494-11ef-951b-9625a5233070",
            }
        ],
    },
    {
        "jobID": "2fe4feaa-8495-11ef-9111-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-07T10:16:16.289Z",
        "started": "2024-10-07T10:16:16.289Z",
        "finished": "2024-10-07T10:16:16.614Z",
        "updated": "2024-10-07T10:16:16.443Z",
        "status": "failed",
        "message": "ZOO-Kernel accepted to run your service!",
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/2fe4feaa-8495-11ef-9111-9625a5233070",
            }
        ],
    },
    {
        "jobID": "2c6c8810-8495-11ef-b86d-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-07T10:16:10.482Z",
        "started": "2024-10-07T10:16:10.482Z",
        "finished": "2024-10-07T10:19:01.308Z",
        "updated": "2024-10-07T10:18:57.662Z",
        "status": "failed",
        "message": 'Unable to run the Service. The message returned back by the Service was the following: Exception during execution...\nTraceback (most recent call last):\n  File "/opt/zooservices_user/eopro_spyro_test/water_bodies/service.py", line 477, in water_bodies\n    exit_status = runner.execute()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/zoo_calrissian_runner/__init__.py", line 451, in execute\n    output = execution.get_output()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/pycalrissian/execution.py", line 84, in get_output\n    return json.load(staged_file)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 293, in load\n    return loads(fp.read(),\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 346, in loads\n    return _default_decoder.decode(s)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 337, in decode\n    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 355, in raw_decode\n    raise JSONDecodeError("Expecting value", s, err.value) from None\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n\n',
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/2c6c8810-8495-11ef-b86d-9625a5233070",
            }
        ],
    },
    {
        "jobID": "cbe36034-849b-11ef-aa82-9625a5233070",
        "type": "process",
        "processID": "raster-calculate",
        "created": "2024-10-07T11:03:34.988Z",
        "started": "2024-10-07T11:03:34.988Z",
        "finished": "2024-10-07T11:06:25.822Z",
        "updated": "2024-10-07T11:06:22.100Z",
        "status": "failed",
        "message": 'Unable to run the Service. The message returned back by the Service was the following: Exception during execution...\nTraceback (most recent call last):\n  File "/opt/zooservices_user/eopro_spyro_test/raster-calculate/service.py", line 477, in raster_calculate\n    exit_status = runner.execute()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/zoo_calrissian_runner/__init__.py", line 451, in execute\n    output = execution.get_output()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/pycalrissian/execution.py", line 84, in get_output\n    return json.load(staged_file)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 293, in load\n    return loads(fp.read(),\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 346, in loads\n    return _default_decoder.decode(s)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 337, in decode\n    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 355, in raw_decode\n    raise JSONDecodeError("Expecting value", s, err.value) from None\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n\n',
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/cbe36034-849b-11ef-aa82-9625a5233070",
            }
        ],
    },
    {
        "jobID": "a403aee0-84a3-11ef-835a-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-07T11:59:44.037Z",
        "started": "2024-10-07T11:59:44.037Z",
        "finished": "2024-10-07T12:02:34.755Z",
        "updated": "2024-10-07T12:02:31.155Z",
        "status": "failed",
        "message": 'Unable to run the Service. The message returned back by the Service was the following: Exception during execution...\nTraceback (most recent call last):\n  File "/opt/zooservices_user/eopro_spyro_test/water_bodies/service.py", line 477, in water_bodies\n    exit_status = runner.execute()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/zoo_calrissian_runner/__init__.py", line 451, in execute\n    output = execution.get_output()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/pycalrissian/execution.py", line 84, in get_output\n    return json.load(staged_file)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 293, in load\n    return loads(fp.read(),\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 346, in loads\n    return _default_decoder.decode(s)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 337, in decode\n    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 355, in raw_decode\n    raise JSONDecodeError("Expecting value", s, err.value) from None\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n\n',
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/a403aee0-84a3-11ef-835a-9625a5233070",
            }
        ],
    },
    {
        "jobID": "31633e86-8495-11ef-ba02-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-07T10:16:18.827Z",
        "started": "2024-10-07T10:16:18.827Z",
        "finished": "2024-10-07T10:19:09.778Z",
        "updated": "2024-10-07T10:19:06.090Z",
        "status": "failed",
        "message": 'Unable to run the Service. The message returned back by the Service was the following: Exception during execution...\nTraceback (most recent call last):\n  File "/opt/zooservices_user/eopro_spyro_test/water_bodies/service.py", line 477, in water_bodies\n    exit_status = runner.execute()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/zoo_calrissian_runner/__init__.py", line 451, in execute\n    output = execution.get_output()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/pycalrissian/execution.py", line 84, in get_output\n    return json.load(staged_file)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 293, in load\n    return loads(fp.read(),\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 346, in loads\n    return _default_decoder.decode(s)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 337, in decode\n    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 355, in raw_decode\n    raise JSONDecodeError("Expecting value", s, err.value) from None\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n\n',
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/31633e86-8495-11ef-ba02-9625a5233070",
            }
        ],
    },
    {
        "jobID": "5b4afc74-84a0-11ef-91ce-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-07T11:36:13.521Z",
        "started": "2024-10-07T11:36:13.521Z",
        "finished": "2024-10-07T11:39:04.332Z",
        "updated": "2024-10-07T11:39:00.686Z",
        "status": "failed",
        "message": 'Unable to run the Service. The message returned back by the Service was the following: Exception during execution...\nTraceback (most recent call last):\n  File "/opt/zooservices_user/eopro_spyro_test/water_bodies/service.py", line 477, in water_bodies\n    exit_status = runner.execute()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/zoo_calrissian_runner/__init__.py", line 451, in execute\n    output = execution.get_output()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/pycalrissian/execution.py", line 84, in get_output\n    return json.load(staged_file)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 293, in load\n    return loads(fp.read(),\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 346, in loads\n    return _default_decoder.decode(s)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 337, in decode\n    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 355, in raw_decode\n    raise JSONDecodeError("Expecting value", s, err.value) from None\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n\n',
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/5b4afc74-84a0-11ef-91ce-9625a5233070",
            }
        ],
    },
    {
        "jobID": "625a76de-84a0-11ef-9c8d-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-07T11:36:25.436Z",
        "started": "2024-10-07T11:36:25.436Z",
        "finished": "2024-10-07T11:39:16.269Z",
        "updated": "2024-10-07T11:39:12.686Z",
        "status": "failed",
        "message": 'Unable to run the Service. The message returned back by the Service was the following: Exception during execution...\nTraceback (most recent call last):\n  File "/opt/zooservices_user/eopro_spyro_test/water_bodies/service.py", line 477, in water_bodies\n    exit_status = runner.execute()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/zoo_calrissian_runner/__init__.py", line 451, in execute\n    output = execution.get_output()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/pycalrissian/execution.py", line 84, in get_output\n    return json.load(staged_file)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 293, in load\n    return loads(fp.read(),\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 346, in loads\n    return _default_decoder.decode(s)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 337, in decode\n    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 355, in raw_decode\n    raise JSONDecodeError("Expecting value", s, err.value) from None\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n\n',
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/625a76de-84a0-11ef-9c8d-9625a5233070",
            }
        ],
    },
    {
        "jobID": "f3317d84-849f-11ef-8221-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-07T11:33:18.894Z",
        "started": "2024-10-07T11:33:18.894Z",
        "finished": "2024-10-07T11:36:09.858Z",
        "updated": "2024-10-07T11:36:06.212Z",
        "status": "failed",
        "message": 'Unable to run the Service. The message returned back by the Service was the following: Exception during execution...\nTraceback (most recent call last):\n  File "/opt/zooservices_user/eopro_spyro_test/water_bodies/service.py", line 477, in water_bodies\n    exit_status = runner.execute()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/zoo_calrissian_runner/__init__.py", line 451, in execute\n    output = execution.get_output()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/pycalrissian/execution.py", line 84, in get_output\n    return json.load(staged_file)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 293, in load\n    return loads(fp.read(),\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 346, in loads\n    return _default_decoder.decode(s)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 337, in decode\n    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 355, in raw_decode\n    raise JSONDecodeError("Expecting value", s, err.value) from None\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n\n',
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/f3317d84-849f-11ef-8221-9625a5233070",
            }
        ],
    },
    {
        "jobID": "fade8db6-849e-11ef-996d-9625a5233070",
        "type": "process",
        "processID": "lulc-change",
        "created": "2024-10-07T11:26:22.279Z",
        "started": "2024-10-07T11:26:22.279Z",
        "finished": "2024-10-07T11:26:22.626Z",
        "updated": "2024-10-07T11:26:22.441Z",
        "status": "failed",
        "message": "ZOO-Kernel accepted to run your service!",
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/fade8db6-849e-11ef-996d-9625a5233070",
            }
        ],
    },
    {
        "jobID": "a2bf4a44-84a3-11ef-a1fc-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-07T11:59:41.913Z",
        "started": "2024-10-07T11:59:41.913Z",
        "finished": "2024-10-07T11:59:42.314Z",
        "updated": "2024-10-07T11:59:42.080Z",
        "status": "failed",
        "message": "ZOO-Kernel accepted to run your service!",
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/a2bf4a44-84a3-11ef-a1fc-9625a5233070",
            }
        ],
    },
    {
        "jobID": "87c9df76-84a6-11ef-81e4-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-07T12:20:25.203Z",
        "started": "2024-10-07T12:20:25.203Z",
        "finished": "2024-10-07T12:20:25.556Z",
        "updated": "2024-10-07T12:20:25.345Z",
        "status": "failed",
        "message": "ZOO-Kernel accepted to run your service!",
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/87c9df76-84a6-11ef-81e4-9625a5233070",
            }
        ],
    },
    {
        "jobID": "8958e81e-84a6-11ef-943e-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-07T12:20:27.790Z",
        "started": "2024-10-07T12:20:27.790Z",
        "finished": "2024-10-07T12:23:18.561Z",
        "updated": "2024-10-07T12:23:14.953Z",
        "status": "failed",
        "message": 'Unable to run the Service. The message returned back by the Service was the following: Exception during execution...\nTraceback (most recent call last):\n  File "/opt/zooservices_user/eopro_spyro_test/water_bodies/service.py", line 477, in water_bodies\n    exit_status = runner.execute()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/zoo_calrissian_runner/__init__.py", line 451, in execute\n    output = execution.get_output()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/pycalrissian/execution.py", line 84, in get_output\n    return json.load(staged_file)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 293, in load\n    return loads(fp.read(),\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 346, in loads\n    return _default_decoder.decode(s)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 337, in decode\n    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 355, in raw_decode\n    raise JSONDecodeError("Expecting value", s, err.value) from None\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n\n',
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/8958e81e-84a6-11ef-943e-9625a5233070",
            }
        ],
    },
    {
        "jobID": "3502618a-84a3-11ef-b757-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-07T11:56:37.857Z",
        "started": "2024-10-07T11:56:37.857Z",
        "finished": "2024-10-07T11:59:28.810Z",
        "updated": "2024-10-07T11:59:25.125Z",
        "status": "failed",
        "message": 'Unable to run the Service. The message returned back by the Service was the following: Exception during execution...\nTraceback (most recent call last):\n  File "/opt/zooservices_user/eopro_spyro_test/water_bodies/service.py", line 477, in water_bodies\n    exit_status = runner.execute()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/zoo_calrissian_runner/__init__.py", line 451, in execute\n    output = execution.get_output()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/pycalrissian/execution.py", line 84, in get_output\n    return json.load(staged_file)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 293, in load\n    return loads(fp.read(),\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 346, in loads\n    return _default_decoder.decode(s)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 337, in decode\n    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 355, in raw_decode\n    raise JSONDecodeError("Expecting value", s, err.value) from None\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n\n',
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/3502618a-84a3-11ef-b757-9625a5233070",
            }
        ],
    },
    {
        "jobID": "60fd2d86-84a0-11ef-9fc7-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-07T11:36:23.107Z",
        "started": "2024-10-07T11:36:23.107Z",
        "finished": "2024-10-07T11:36:23.475Z",
        "updated": "2024-10-07T11:36:23.281Z",
        "status": "failed",
        "message": "ZOO-Kernel accepted to run your service!",
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/60fd2d86-84a0-11ef-9fc7-9625a5233070",
            }
        ],
    },
    {
        "jobID": "1a1be6fe-84a6-11ef-b45e-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-07T12:17:21.164Z",
        "started": "2024-10-07T12:17:21.164Z",
        "finished": "2024-10-07T12:20:11.090Z",
        "updated": "2024-10-07T12:20:08.324Z",
        "status": "failed",
        "message": 'Unable to run the Service. The message returned back by the Service was the following: Exception during execution...\nTraceback (most recent call last):\n  File "/opt/zooservices_user/eopro_spyro_test/water_bodies/service.py", line 477, in water_bodies\n    exit_status = runner.execute()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/zoo_calrissian_runner/__init__.py", line 451, in execute\n    output = execution.get_output()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/pycalrissian/execution.py", line 84, in get_output\n    return json.load(staged_file)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 293, in load\n    return loads(fp.read(),\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 346, in loads\n    return _default_decoder.decode(s)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 337, in decode\n    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 355, in raw_decode\n    raise JSONDecodeError("Expecting value", s, err.value) from None\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n\n',
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/1a1be6fe-84a6-11ef-b45e-9625a5233070",
            }
        ],
    },
    {
        "jobID": "9cca235c-84a3-11ef-95c6-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-07T11:59:32.021Z",
        "started": "2024-10-07T11:59:32.021Z",
        "finished": "2024-10-07T12:02:23.001Z",
        "updated": "2024-10-07T12:02:19.282Z",
        "status": "failed",
        "message": 'Unable to run the Service. The message returned back by the Service was the following: Exception during execution...\nTraceback (most recent call last):\n  File "/opt/zooservices_user/eopro_spyro_test/water_bodies/service.py", line 477, in water_bodies\n    exit_status = runner.execute()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/zoo_calrissian_runner/__init__.py", line 451, in execute\n    output = execution.get_output()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/pycalrissian/execution.py", line 84, in get_output\n    return json.load(staged_file)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 293, in load\n    return loads(fp.read(),\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 346, in loads\n    return _default_decoder.decode(s)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 337, in decode\n    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 355, in raw_decode\n    raise JSONDecodeError("Expecting value", s, err.value) from None\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n\n',
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/9cca235c-84a3-11ef-95c6-9625a5233070",
            }
        ],
    },
    {
        "jobID": "81ceac96-84a6-11ef-93d2-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-07T12:20:15.125Z",
        "started": "2024-10-07T12:20:15.125Z",
        "finished": "2024-10-07T12:23:06.901Z",
        "updated": "2024-10-07T12:23:02.238Z",
        "status": "failed",
        "message": 'Unable to run the Service. The message returned back by the Service was the following: Exception during execution...\nTraceback (most recent call last):\n  File "/opt/zooservices_user/eopro_spyro_test/water_bodies/service.py", line 477, in water_bodies\n    exit_status = runner.execute()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/zoo_calrissian_runner/__init__.py", line 451, in execute\n    output = execution.get_output()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/pycalrissian/execution.py", line 84, in get_output\n    return json.load(staged_file)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 293, in load\n    return loads(fp.read(),\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 346, in loads\n    return _default_decoder.decode(s)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 337, in decode\n    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 355, in raw_decode\n    raise JSONDecodeError("Expecting value", s, err.value) from None\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n\n',
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/81ceac96-84a6-11ef-93d2-9625a5233070",
            }
        ],
    },
    {
        "jobID": "9dc5fb8e-85a5-11ef-93b3-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-08T18:46:23.799Z",
        "started": "2024-10-08T18:46:23.799Z",
        "finished": "2024-10-08T18:49:14.574Z",
        "updated": "2024-10-08T18:49:10.848Z",
        "status": "failed",
        "message": 'Unable to run the Service. The message returned back by the Service was the following: Exception during execution...\nTraceback (most recent call last):\n  File "/opt/zooservices_user/eopro_spyro_test/water_bodies/service.py", line 477, in water_bodies\n    exit_status = runner.execute()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/zoo_calrissian_runner/__init__.py", line 451, in execute\n    output = execution.get_output()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/pycalrissian/execution.py", line 84, in get_output\n    return json.load(staged_file)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 293, in load\n    return loads(fp.read(),\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 346, in loads\n    return _default_decoder.decode(s)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 337, in decode\n    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 355, in raw_decode\n    raise JSONDecodeError("Expecting value", s, err.value) from None\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n\n',
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/9dc5fb8e-85a5-11ef-93b3-9625a5233070",
            }
        ],
    },
    {
        "jobID": "2ff477de-85a5-11ef-b762-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-08T18:43:19.501Z",
        "started": "2024-10-08T18:43:19.501Z",
        "finished": "2024-10-08T18:46:09.210Z",
        "updated": "2024-10-08T18:46:06.650Z",
        "status": "failed",
        "message": 'Unable to run the Service. The message returned back by the Service was the following: Exception during execution...\nTraceback (most recent call last):\n  File "/opt/zooservices_user/eopro_spyro_test/water_bodies/service.py", line 477, in water_bodies\n    exit_status = runner.execute()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/zoo_calrissian_runner/__init__.py", line 451, in execute\n    output = execution.get_output()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/pycalrissian/execution.py", line 84, in get_output\n    return json.load(staged_file)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 293, in load\n    return loads(fp.read(),\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 346, in loads\n    return _default_decoder.decode(s)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 337, in decode\n    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 355, in raw_decode\n    raise JSONDecodeError("Expecting value", s, err.value) from None\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n\n',
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/2ff477de-85a5-11ef-b762-9625a5233070",
            }
        ],
    },
    {
        "jobID": "9c0ce596-85a5-11ef-a668-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-08T18:46:20.939Z",
        "started": "2024-10-08T18:46:20.939Z",
        "finished": "2024-10-08T18:46:21.432Z",
        "updated": "2024-10-08T18:46:21.193Z",
        "status": "failed",
        "message": "ZOO-Kernel accepted to run your service!",
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/9c0ce596-85a5-11ef-a668-9625a5233070",
            }
        ],
    },
    {
        "jobID": "ad5a6d2a-85a3-11ef-950b-9625a5233070",
        "type": "process",
        "processID": "raster-calculate",
        "created": "2024-10-08T18:32:30.903Z",
        "started": "2024-10-08T18:32:30.903Z",
        "finished": "2024-10-08T18:32:31.372Z",
        "updated": "2024-10-08T18:32:31.179Z",
        "status": "failed",
        "message": "ZOO-Kernel accepted to run your service!",
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/ad5a6d2a-85a3-11ef-950b-9625a5233070",
            }
        ],
    },
    {
        "jobID": "97e571fe-85a5-11ef-8bed-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-08T18:46:13.861Z",
        "started": "2024-10-08T18:46:13.861Z",
        "finished": "2024-10-08T18:49:03.826Z",
        "updated": "2024-10-08T18:49:01.074Z",
        "status": "failed",
        "message": 'Unable to run the Service. The message returned back by the Service was the following: Exception during execution...\nTraceback (most recent call last):\n  File "/opt/zooservices_user/eopro_spyro_test/water_bodies/service.py", line 477, in water_bodies\n    exit_status = runner.execute()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/zoo_calrissian_runner/__init__.py", line 451, in execute\n    output = execution.get_output()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/pycalrissian/execution.py", line 84, in get_output\n    return json.load(staged_file)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 293, in load\n    return loads(fp.read(),\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 346, in loads\n    return _default_decoder.decode(s)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 337, in decode\n    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 355, in raw_decode\n    raise JSONDecodeError("Expecting value", s, err.value) from None\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n\n',
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/97e571fe-85a5-11ef-8bed-9625a5233070",
            }
        ],
    },
    {
        "jobID": "42a3204e-87ce-11ef-b2c1-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-11T12:42:22.620Z",
        "started": "2024-10-11T12:42:22.620Z",
        "finished": "2024-10-11T12:45:13.449Z",
        "updated": "2024-10-11T12:45:09.732Z",
        "status": "failed",
        "message": 'Unable to run the Service. The message returned back by the Service was the following: Exception during execution...\nTraceback (most recent call last):\n  File "/opt/zooservices_user/eopro_spyro_test/water_bodies/service.py", line 477, in water_bodies\n    exit_status = runner.execute()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/zoo_calrissian_runner/__init__.py", line 451, in execute\n    output = execution.get_output()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/pycalrissian/execution.py", line 84, in get_output\n    return json.load(staged_file)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 293, in load\n    return loads(fp.read(),\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 346, in loads\n    return _default_decoder.decode(s)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 337, in decode\n    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 355, in raw_decode\n    raise JSONDecodeError("Expecting value", s, err.value) from None\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n\n',
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/42a3204e-87ce-11ef-b2c1-9625a5233070",
            }
        ],
    },
    {
        "jobID": "b0b4db7c-87ce-11ef-9b27-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-11T12:45:27.243Z",
        "started": "2024-10-11T12:45:27.243Z",
        "finished": "2024-10-11T12:48:23.025Z",
        "updated": "2024-10-11T12:48:14.325Z",
        "status": "failed",
        "message": 'Unable to run the Service. The message returned back by the Service was the following: Exception during execution...\nTraceback (most recent call last):\n  File "/opt/zooservices_user/eopro_spyro_test/water_bodies/service.py", line 477, in water_bodies\n    exit_status = runner.execute()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/zoo_calrissian_runner/__init__.py", line 451, in execute\n    output = execution.get_output()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/pycalrissian/execution.py", line 84, in get_output\n    return json.load(staged_file)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 293, in load\n    return loads(fp.read(),\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 346, in loads\n    return _default_decoder.decode(s)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 337, in decode\n    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 355, in raw_decode\n    raise JSONDecodeError("Expecting value", s, err.value) from None\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n\n',
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/b0b4db7c-87ce-11ef-9b27-9625a5233070",
            }
        ],
    },
    {
        "jobID": "af672054-87ce-11ef-919d-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-11T12:45:25.043Z",
        "started": "2024-10-11T12:45:25.043Z",
        "finished": "2024-10-11T12:45:25.450Z",
        "updated": "2024-10-11T12:45:25.215Z",
        "status": "failed",
        "message": "ZOO-Kernel accepted to run your service!",
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/af672054-87ce-11ef-919d-9625a5233070",
            }
        ],
    },
    {
        "jobID": "ab7fe35e-87ce-11ef-8f4b-9625a5233070",
        "type": "process",
        "processID": "water_bodies",
        "created": "2024-10-11T12:45:18.490Z",
        "started": "2024-10-11T12:45:18.490Z",
        "finished": "2024-10-11T12:48:10.384Z",
        "updated": "2024-10-11T12:48:05.707Z",
        "status": "failed",
        "message": 'Unable to run the Service. The message returned back by the Service was the following: Exception during execution...\nTraceback (most recent call last):\n  File "/opt/zooservices_user/eopro_spyro_test/water_bodies/service.py", line 477, in water_bodies\n    exit_status = runner.execute()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/zoo_calrissian_runner/__init__.py", line 451, in execute\n    output = execution.get_output()\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/site-packages/pycalrissian/execution.py", line 84, in get_output\n    return json.load(staged_file)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 293, in load\n    return loads(fp.read(),\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/__init__.py", line 346, in loads\n    return _default_decoder.decode(s)\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 337, in decode\n    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\n  File "/usr/miniconda3/envs/env_zoo_calrissian/lib/python3.10/json/decoder.py", line 355, in raw_decode\n    raise JSONDecodeError("Expecting value", s, err.value) from None\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n\n',
        "links": [
            {
                "title": "Status location",
                "rel": "monitor",
                "type": "application/json",
                "href": "https://test.eodatahub.org.uk/ades/eopro_spyro_test/ogc-api/jobs/ab7fe35e-87ce-11ef-8f4b-9625a5233070",
            }
        ],
    },
]
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
        *GET_ALL_FAILED_JOBS_RESPONSE,
        GET_JOB_FINISHED_STATUS_RESPONSE,
        GET_JOB_IN_PROGRESS_STATUS_RESPONSE,
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

    async def list_job_submissions(
        self,
        *,
        raw_output: bool = False,
    ) -> tuple[ErrorResponse | None, JobList | dict[str, Any] | None]:
        return None, GET_JOB_LIST_RESPONSE if raw_output else JobList(**GET_JOB_LIST_RESPONSE)

    async def cancel_job(self, job_id: str | UUID) -> tuple[ErrorResponse | None, StatusInfo | None]:
        job = StatusInfo(**GET_JOB_FINISHED_STATUS_RESPONSE)
        job.status = StatusCode.dismissed
        return None, job

    async def register_process_from_cwl_href_with_download(
        self,
        cwl_href: str,
        id_override: str | None = None,
    ) -> tuple[ErrorResponse | None, ProcessSummary | None]:
        return None, ProcessSummary(**REGISTER_PROCESS_RESPONSE)

    async def register_process_from_local_cwl_file(
        self,
        cwl_location: Path,
        id_override: str | None = None,
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

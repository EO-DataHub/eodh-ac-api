from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Link(BaseModel):
    rel: str
    type: str
    href: str
    title: str | None = None


class Metadatum(BaseModel):
    title: str | None = None
    role: str | None = None
    value: str | None = None


class Schema(BaseModel):
    type: str
    nullable: bool | None = None


class Input(BaseModel):
    title: str
    description: str
    schema_: Schema = Field(..., alias="schema")


class Type(BaseModel):
    enum: list[str]


class Properties(BaseModel):
    type: Type


class AllOfItem(BaseModel):
    ref: str | None = Field(None, alias="$ref")
    type: str | None = None
    properties: Properties | None = None


class Process(BaseModel):
    id: str
    title: str
    description: str
    mutable: bool
    version: str
    job_control_options: list[str] = Field(..., alias="jobControlOptions")
    output_transmission: list[str] = Field(..., alias="outputTransmission")
    links: list[Link]
    metadata: list[Metadatum] | None = None


class AdesProcessesResponse(BaseModel):
    processes: list[Process]
    links: list[Link]
    number_total: int = Field(..., alias="numberTotal")


class AdesJobResponse(BaseModel):
    job_id: str = Field(..., alias="jobID")
    type: str
    process_id: str = Field(..., alias="processID")
    created: str
    started: str
    finished: str
    updated: str
    status: str
    message: str
    links: list[Link]


class AdesJobSubmissionsResponse(BaseModel):
    jobs: list[AdesJobResponse]
    links: list[Link]
    number_total: int = Field(..., alias="numberTotal")


class OneOfItem(BaseModel):
    all_of: list[AllOfItem] | None = Field(None, alias="allOf")
    type: str | None = None
    required: list[str] | None = None
    properties: Properties | None = None


class ExtendedSchema(BaseModel):
    one_of: list[OneOfItem] = Field(..., alias="oneOf")


class Results(BaseModel):
    title: str
    description: str
    extended_schema: ExtendedSchema = Field(..., alias="extended-schema")
    schema_: Schema = Field(..., alias="schema")


class Outputs(BaseModel):
    results: Results


class AdesProcessDetailsResponse(BaseModel):
    id: str
    title: str
    description: str
    mutable: bool
    version: str
    metadata: list[Metadatum]
    output_transmission: list[str] = Field(..., alias="outputTransmission")
    job_control_options: list[str] = Field(..., alias="jobControlOptions")
    links: list[Link]
    inputs: dict[str, Input]
    outputs: Outputs


class AdesJobExecutionErrorResponse(BaseModel):
    title: str
    type: str
    detail: str


class AdesJobExecutionResultsResponse(BaseModel):
    results: dict[str, Any]

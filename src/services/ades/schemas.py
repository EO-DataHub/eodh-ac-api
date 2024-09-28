from __future__ import annotations

from enum import Enum
from typing import Annotated, Any, Dict, List, Optional, Union

from pydantic import (
    AnyUrl,
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    PositiveFloat,
    RootModel,
)


class AdesException(BaseModel):
    """JSON schema for exceptions based on RFC 7807."""

    model_config = ConfigDict(
        extra="allow",
    )
    type: str
    title: str | None = None
    status: int | None = None
    detail: str | None = None
    instance: str | None = None


class ConfClasses(BaseModel):
    conforms_to: list[str] = Field(..., alias="conformsTo")


class Response(Enum):
    raw = "raw"
    document = "document"


class JobType(Enum):
    process = "process"


class Link(BaseModel):
    href: str
    rel: str | None = Field(None, examples=["service"])
    type: str | None = Field(None, examples=["application/json"])
    hreflang: str | None = Field(None, examples=["en"])
    title: str | None = None


class MaxOccurs(Enum):
    unbounded = "unbounded"


class Subscriber(BaseModel):
    """Optional URIs for callbacks for this job.

    Support for this parameter is not required and the parameter may be removed from the API definition, if conformance
    class **'callback'** is not listed in the conformance declaration under `/conformance`.

    """

    success_uri: AnyUrl | None = Field(None, alias="successUri")
    in_progress_uri: AnyUrl | None = Field(None, alias="inProgressUri")
    failed_uri: AnyUrl | None = Field(None, alias="failedUri")


class StatusCode(Enum):
    accepted = "accepted"
    running = "running"
    successful = "successful"
    failed = "failed"
    dismissed = "dismissed"


class JobControlOptions(Enum):
    sync_execute = "sync-execute"
    async_execute = "async-execute"
    dismiss = "dismiss"


class TransmissionMode(Enum):
    value = "value"
    reference = "reference"


class DataType(Enum):
    array = "array"
    boolean = "boolean"
    integer = "integer"
    number = "number"
    object = "object"
    string = "string"


class Format(BaseModel):
    media_type: str | None = Field(None, alias="mediaType")
    encoding: str | None = None
    schema_: str | dict[str, Any] | None = Field(None, alias="schema")


class Metadata(BaseModel):
    title: str | None = None
    role: str | None = None
    href: str | None = None


class AdditionalParameter(BaseModel):
    name: str
    value: list[str | float | int | list[dict[str, Any]] | dict[str, Any]]


class Reference(BaseModel):
    field_ref: str = Field(..., alias="$ref")


class BinaryInputValue(RootModel[str]):
    root: str


class Crs(Enum):
    crs84 = "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
    crs84h = "http://www.opengis.net/def/crs/OGC/0/CRS84h"


class Bbox(BaseModel):
    bbox: list[float]
    crs: Crs | None = Crs.crs84


class LandingPage(BaseModel):
    title: str | None = Field(None, examples=["Example processing server"])
    description: str | None = Field(
        None,
        examples=["Example server implementing the OGC API - Processes 1.0 Standard"],
    )
    links: list[Link]


class StatusInfo(BaseModel):
    process_id: str | None = Field(None, alias="processID")
    type: JobType
    job_id: str = Field(..., alias="jobID")
    status: StatusCode
    message: str | None = None
    created: AwareDatetime | None = None
    started: AwareDatetime | None = None
    finished: AwareDatetime | None = None
    updated: AwareDatetime | None = None
    progress: Annotated[int | None, Field(None, strict=True, ge=0, le=100)]
    links: list[Link] | None = None


class Output(BaseModel):
    format: Format | None = None
    transmission_mode: TransmissionMode | None = Field("value", alias="transmissionMode")


class AdditionalParameters(Metadata):
    parameters: list[AdditionalParameter] | None = None


class DescriptionType(BaseModel):
    title: str | None = None
    description: str | None = None
    keywords: list[str] | None = None
    metadata: list[Metadata] | None = None
    additional_parameters: AdditionalParameters | None = Field(None, alias="additionalParameters")


class InputValueNoObject(RootModel[Union[str, float, int, bool, List[str], BinaryInputValue, Bbox]]):
    root: str | float | int | bool | list[str] | BinaryInputValue | Bbox


class InputValue(RootModel[Union[InputValueNoObject, Dict[str, Any]]]):
    root: InputValueNoObject | dict[str, Any]


class JobList(BaseModel):
    jobs: list[StatusInfo]
    links: list[Link]
    number_total: int = Field(..., alias="numberTotal")


class ProcessSummary(DescriptionType):
    id: str
    version: str
    job_control_options: list[JobControlOptions] | None = Field(None, alias="jobControlOptions")
    output_transmission: list[TransmissionMode] | None = Field(None, alias="outputTransmission")
    links: list[Link] | None = None


class QualifiedInputValue(Format):
    value: InputValue


class ProcessList(BaseModel):
    processes: list[ProcessSummary]
    links: list[Link]


class ExecutionUnit(BaseModel):
    href: str
    type: str = "application/cwl"


class RegisterProcessRequest(BaseModel):
    execution_unit: ExecutionUnit = Field(..., alias="executionUnit")


class InlineOrRefData(RootModel[Union[InputValueNoObject, QualifiedInputValue, Link]]):
    root: InputValueNoObject | QualifiedInputValue | Link


class Execute(BaseModel):
    inputs: dict[str, InlineOrRefData | list[InlineOrRefData]] | None = None
    outputs: dict[str, Output] | None = None
    response: Response | None = Response.raw
    subscriber: Subscriber | None = None


class Results(RootModel[Optional[Dict[str, InlineOrRefData]]]):
    root: dict[str, InlineOrRefData] | None = None


class InlineResponse200(RootModel[Union[str, float, int, Dict[str, Any], List[Dict[str, Any]], bool, bytes, Results]]):
    root: str | float | int | dict[str, Any] | list[dict[str, Any]] | bool | bytes | Results


class Process(ProcessSummary):
    inputs: dict[str, InputDescription] | None = None
    outputs: dict[str, OutputDescription] | None = None


class InputDescription(DescriptionType):
    min_occurs: int | None = Field(1, alias="minOccurs")
    max_occurs: int | MaxOccurs | None = Field(None, alias="maxOccurs")
    schema_: Schema = Field(..., alias="schema")


class OutputDescription(DescriptionType):
    schema_: Schema = Field(..., alias="schema")


class SchemaModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    title: str | None = None
    multiple_of: PositiveFloat | None = Field(None, alias="multipleOf")
    maximum: float | None = None
    exclusive_maximum: bool | None = Field(default=False, alias="exclusiveMaximum")
    minimum: float | None = None
    exclusive_minimum: bool | None = Field(default=False, alias="exclusiveMinimum")
    max_length: Annotated[int | None, Field(None, alias="maxLength", ge=0)]
    min_length: Annotated[int | None, Field(0, alias="minLength", ge=0)]
    pattern: str | None = None
    max_items: Annotated[int | None, Field(None, alias="maxItems", ge=0)]
    min_items: Annotated[int | None, Field(0, alias="minItems", ge=0)]
    unique_items: bool | None = Field(default=False, alias="uniqueItems")
    max_properties: Annotated[int | None, Field(None, alias="maxProperties", ge=0)]
    min_properties: Annotated[int | None, Field(0, alias="minProperties", ge=0)]
    required: list[str] | None = Field(None, min_length=1)
    enum: list[dict[str, Any]] | None = Field(None, min_length=1)
    type: DataType | None = None
    not_: Schema | Reference | None = Field(None, alias="not")
    all_of: list[Schema | Reference] | None = Field(None, alias="allOf")
    one_of: list[Schema | Reference] | None = Field(None, alias="oneOf")
    any_of: list[Schema | Reference] | None = Field(None, alias="anyOf")
    items: Schema | Reference | None = None
    properties: dict[str, Schema | Reference] | None = None
    additional_properties: Schema | Reference | bool | None = Field(default=True, alias="additionalProperties")
    description: str | None = None
    format: str | None = None
    default: dict[str, Any] | None = None
    nullable: bool | None = False
    read_only: bool | None = Field(default=False, alias="readOnly")
    write_only: bool | None = Field(default=False, alias="writeOnly")
    example: dict[str, Any] | None = None
    deprecated: bool | None = False
    content_media_type: str | None = Field(None, alias="contentMediaType")
    content_encoding: str | None = Field(None, alias="contentEncoding")
    content_schema: str | None = Field(None, alias="contentSchema")


class Schema(RootModel[Union[Reference, SchemaModel]]):
    root: Reference | SchemaModel


class JobExecutionResults(BaseModel):
    results: dict[str, Any] | AdesException


Process.model_rebuild()
InputDescription.model_rebuild()
OutputDescription.model_rebuild()
SchemaModel.model_rebuild()

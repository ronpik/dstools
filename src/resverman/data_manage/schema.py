from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

import numpy as np
from PIL.Image import Image
from typing_extensions import Self

from app.common.ext.typing_ext import JSON
from app.schemas.ocr import ProcessedOCRData
from app.schemas.results.layout import LayoutResult
from research.common.json_tools.json_handler import serialize_json_as_dict, deserialize_json


class LocationType(Enum):
    GCS = "GCS"
    ZARR = "ZARR"


@dataclass(frozen=True)
class ContentLocation:
    location: str
    location_type: str

@dataclass(frozen=True)
class DocumentRecord:
    doc_id: str
    doc_info: dict[str, Any]
    content_location: ContentLocation

@dataclass(frozen=True)
class DocumentRecordWithContent(DocumentRecord):
    content: Image


@dataclass(frozen=True)
class DataDBRecord:
    id: str

    def to_json(self) -> dict[str, JSON]:
        return serialize_json_as_dict(self)

    @classmethod
    def from_json(cls, json_dict: dict[str, Any]) -> Self:
        return deserialize_json(json_dict, cls)


@dataclass(frozen=True)
class DataDBRecordWithContent(DataDBRecord):
    pass


@dataclass(frozen=True)
class RawPageRecord(DataDBRecord):
    page_id: Optional[str] = None
    page_hash: Optional[str] = None
    size: Optional[int] = None
    image_format: Optional[str] = None
    image: Optional[Image] = None


@dataclass(frozen=True)
class RawPageMetadataRecord(DataDBRecord):
    page_id: Optional[str] = None
    page_hash: Optional[str] = None
    size: Optional[int] = None
    image_format: Optional[str] = None
    location_type: Optional[LocationType] = None
    content_location: Optional[str] = None


@dataclass(frozen=True)
class EnrichedPageRecord(DataDBRecord):
    page_id: Optional[str] = None
    page_hash: Optional[str] = None
    yolo_v10_dla_e: Optional[np.ndarray] = None
    fp_prob: Optional[float] = None
    gv_ocr: Optional[ProcessedOCRData] = None
    reducto: Optional[LayoutResult] = None

    def to_json(self) -> dict[str, JSON]:
        dict_record = super().to_json()
        if self.yolo_v10_dla_e is not None:
            dict_record["yolo_v10_dla_e"] = self.yolo_v10_dla_e.tobytes().hex()

        return dict_record

    @classmethod
    def from_json(cls, json_dict: dict[str, Any]) -> Self:
        yolo_hex = json_dict.get("yolo_v10_dla_e")
        if yolo_hex is not None:
            yolo_bytes = bytes.fromhex(yolo_hex)
            json_dict["yolo_v10_dla_e"] = np.frombuffer(yolo_bytes, dtype=np.float32)

        return super().from_json(json_dict)


@dataclass(frozen=True)
class DocumentRecord(DataDBRecord):
    n_pages: Optional[int]
    pages: Optional[list[str]]


@dataclass(frozen=True)
class PackageRecord(DataDBRecord):
    n_pages: Optional[int]
    pages: Optional[list[str]]

"""Opt-in FIT recorder relabelling; the source is never written."""

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from tempfile import TemporaryDirectory
from types import MappingProxyType

from fit_tool.fit_file import FitFile
from fit_tool.fit_file_builder import FitFileBuilder
from fit_tool.fit_file_header import FitFileHeader
from fit_tool.profile.messages.device_info_message import DeviceInfoMessage
from fit_tool.profile.messages.file_id_message import FileIdMessage
from fit_tool.profile.profile_type import FileType, GarminProduct, Manufacturer
from fit_tool.utils.crc import crc16

from .errors import GarminCliError


@dataclass(frozen=True)
class DeviceProfile:
    label: str
    product: int


# Garmin SDK profile, pinned verification source (4024 is FR955, not Edge 840):
# https://github.com/garmin/fit-python-sdk/blob/7e4b3132d50de66f5adfcd6c0addeaade41536d4/garmin_fit_sdk/profile.py
DEVICE_PROFILES = MappingProxyType(
    {
        "edge-530": DeviceProfile("Edge 530", GarminProduct.EDGE_530.value),
        "edge-840": DeviceProfile("Edge 840", 4062),
        "forerunner-955": DeviceProfile("Forerunner 955", 4024),
    }
)
DeviceModel = Enum(
    "DeviceModel", {name.replace("-", "_"): name for name in DEVICE_PROFILES}, type=str
)


def _content(messages: list) -> list:
    """Compare encoded field values, including developer fields, across rebuilds."""
    return [
        (
            message.global_id,
            {
                (kind, getattr(field, "developer_data_index", None), field.field_id): (
                    field.base_type,
                    field.to_bytes(endian=message.endian),
                )
                for kind, fields in (
                    ("native", message.fields),
                    ("developer", message.developer_fields),
                )
                for field in fields
                if field.size
            },
        )
        for message in messages
    ]


def _messages(fit: FitFile) -> list:
    return [record.message for record in fit.records if not record.is_definition]


def _transform(data: bytes, profile: DeviceProfile) -> bytes:
    if len(data) < 14 or data[0] not in (12, 14) or data[8:12] != b".FIT":
        raise ValueError("Invalid FIT header")
    if data[0] + int.from_bytes(data[4:8], "little") + 2 != len(data):
        raise ValueError("Invalid FIT declared length")
    if data[0] == 14 and data[12:14] != b"\0\0":
        if crc16(data[:12]) != int.from_bytes(data[12:14], "little"):
            raise ValueError("Invalid FIT header CRC")
    parsed = FitFile.from_bytes(data)
    # fit-tool skips unknown fields in known messages and cannot safely decode
    # compressed timestamps. Require a byte-exact *unmodified* roundtrip first.
    # This also rejects trailing/concatenated files and unrepresented content.
    if (
        any(r.header.is_time_compressed for r in parsed.records)
        or parsed.to_bytes() != data
    ):
        raise ValueError("FIT content cannot roundtrip losslessly")
    messages = _messages(parsed)
    identities = [m for m in messages if isinstance(m, FileIdMessage)]
    if (
        len(identities) != 1
        or messages[0] is not identities[0]
        or identities[0].get_field_by_name("type").size != 1
        or identities[0].type != FileType.ACTIVITY.value
    ):
        raise ValueError("Expected one leading activity file identity")
    for message in messages:
        # The library decodes known fields using its profile's type, even if
        # the input definition declares a different type. Don't normalize it.
        for definition in message.definition_message.field_definitions:
            field = message.get_field(definition.field_id)
            if field.base_type != definition.base_type:
                raise ValueError("Unsupported FIT field encoding")
        if isinstance(message, DeviceInfoMessage):
            if message.get_field_by_name("device_index").size not in (0, 1):
                raise ValueError("Ambiguous device index")
        if isinstance(message, FileIdMessage) or (
            isinstance(message, DeviceInfoMessage) and message.device_index == 0
        ):
            for name, value in (
                ("manufacturer", Manufacturer.GARMIN.value),
                ("product", profile.product),
            ):
                field = message.get_field_by_name(name)
                if field.size not in (0, 2):
                    raise ValueError("Ambiguous recorder identity")
                field.growable = True
                setattr(message, name, value)
            # Rebuild only these definitions, allowing absent identity fields.
            # Other records may share the decoded definition: don't mutate it.
            message.definition_message = None
    expected = _content(messages)
    builder = FitFileBuilder(auto_define=True)
    builder.add_all(messages)
    rebuilt = builder.build()
    rebuilt.header = FitFileHeader(
        records_size=rebuilt.header.records_size,
        protocol_version=parsed.header.protocol_version,
        profile_version=parsed.header.profile_version,
        gen_crc=parsed.header.crc is not None,
    )
    rebuilt.crc = None
    result = rebuilt.to_bytes()
    if _content(_messages(FitFile.from_bytes(result))) != expected:
        raise ValueError("FIT content changed during rebuild")
    return result


@contextmanager
def prepare_fit(source: str | Path, model: str) -> Iterator[Path]:
    """Yield a private upload copy, removing it even if upload is interrupted."""
    try:
        profile = DEVICE_PROFILES[model]
    except KeyError:
        raise GarminCliError(
            f"Unsupported device profile {model!r}; choose {', '.join(DEVICE_PROFILES)}."
        ) from None
    try:
        transformed = _transform(Path(source).read_bytes(), profile)
    except Exception as exc:
        # fit-tool uses generic exceptions; don't expose source content in errors.
        raise GarminCliError(
            "Cannot prepare FIT: malformed, nonactivity, or unsupported content; "
            "a lossless roundtrip and one activity file identity are required."
        ) from exc
    try:
        temporary = TemporaryDirectory(prefix="gc-fit-")
    except OSError as exc:
        raise GarminCliError("Cannot create temporary FIT upload copy.") from exc
    with temporary as directory:
        prepared = Path(directory) / "upload.fit"
        try:
            with prepared.open("xb") as stream:
                prepared.chmod(0o600)
                stream.write(transformed)
        except OSError as exc:
            raise GarminCliError("Cannot write temporary FIT upload copy.") from exc
        yield prepared

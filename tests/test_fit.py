import hashlib
import stat

import pytest
from fit_tool.fit_file import FitFile
from fit_tool.fit_file_builder import FitFileBuilder
from fit_tool.profile.messages.device_info_message import DeviceInfoMessage
from fit_tool.profile.messages.file_id_message import FileIdMessage
from fit_tool.profile.messages.record_message import RecordMessage

from garmincli.errors import GarminCliError
from garmincli.fit import prepare_fit
from fit_fixtures import activity_bytes


def messages(data):
    return [r.message for r in FitFile.from_bytes(data).records if not r.is_definition]


def values(message):
    return {
        (kind, getattr(f, "developer_data_index", None), f.field_id): f.get_values()
        for kind, fields in [
            ("native", message.fields),
            ("developer", message.developer_fields),
        ]
        for f in fields
        if f.size
    }


@pytest.mark.parametrize(
    "profile,product",
    [("edge-530", 3121), ("edge-840", 4062), ("forerunner-955", 4024)],
)
@pytest.mark.parametrize(
    "devices,developer,unknown,hr",
    [(True, True, False, False), (False, False, True, True)],
)
def test_only_recorder_identity_changes(
    tmp_path, profile, product, devices, developer, unknown, hr
):
    original = activity_bytes(
        devices=devices, developer=developer, unknown=unknown, hr=hr
    )
    source = tmp_path / "original.fit"
    source.write_bytes(original)
    digest = hashlib.sha256(original).hexdigest()
    before = messages(original)
    with prepare_fit(source, profile) as prepared:
        assert prepared != source
        assert prepared.suffix == ".fit"
        assert stat.S_IMODE(prepared.stat().st_mode) == 0o600
        assert stat.S_IMODE(prepared.parent.stat().st_mode) == 0o700
        after = messages(prepared.read_bytes())  # independent decode also checks CRC
        assert len(before) == len(after)
        for old, new in zip(before, after):
            assert old.global_id == new.global_id
            expected = values(old)
            if isinstance(old, FileIdMessage) or (
                isinstance(old, DeviceInfoMessage) and old.device_index == 0
            ):
                manufacturer_id = 1 if isinstance(old, FileIdMessage) else 2
                product_id = 2 if isinstance(old, FileIdMessage) else 4
                expected["native", None, manufacturer_id] = [1]
                expected["native", None, product_id] = [product]
            assert values(new) == expected
        for record in (m for m in after if isinstance(m, RecordMessage)):
            assert (record.heart_rate is not None) == hr
    assert not prepared.exists()
    assert not prepared.parent.exists()
    assert hashlib.sha256(source.read_bytes()).hexdigest() == digest


@pytest.mark.parametrize("error", [RuntimeError, KeyboardInterrupt])
def test_cleanup_when_caller_fails(tmp_path, error):
    source = tmp_path / "source.fit"
    source.write_bytes(activity_bytes())
    with pytest.raises(error):
        with prepare_fit(source, "edge-530") as prepared:
            raise error("synthetic failure")
    assert not prepared.exists()
    assert not prepared.parent.exists()


@pytest.mark.parametrize(
    "case",
    [
        "garbage",
        "truncated",
        "crc",
        "trailing",
        "nonactivity",
        "missing",
        "duplicate",
        "unknown-field",
    ],
)
def test_reject_unsafe_files(tmp_path, case):
    original = activity_bytes()
    if case == "garbage":
        data = b"<gpx></gpx>"
    elif case == "truncated":
        data = original[:-5]
    elif case == "crc":
        data = original[:-1] + bytes([original[-1] ^ 1])
    elif case == "trailing":
        data = original + b"extra"
    else:
        decoded = messages(original)
        if case == "nonactivity":
            decoded[0].type = 6  # course
        elif case == "missing":
            decoded = decoded[1:]
        elif case == "duplicate":
            decoded.append(decoded[0])
        elif case == "unknown-field":
            from fit_tool.base_type import BaseType
            from fit_tool.field import Field

            decoded[0].definition_message = None
            field = Field(field_id=240, base_type=BaseType.UINT16, size=2)
            field.set_value(0, 456)
            decoded[0].fields.append(field)
        builder = FitFileBuilder()
        builder.add_all(decoded)
        data = builder.build().to_bytes()
    source = tmp_path / "bad.fit"
    source.write_bytes(data)
    with pytest.raises(GarminCliError, match="FIT"):
        with prepare_fit(source, "edge-530"):
            pytest.fail("must not yield unsafe input")
    assert source.read_bytes() == data


def test_unknown_profile_and_missing_source(tmp_path):
    with pytest.raises(GarminCliError, match="profile"):
        with prepare_fit(tmp_path / "missing.fit", "edge-999"):
            pytest.fail("must not yield")
    with pytest.raises(GarminCliError, match="FIT"):
        with prepare_fit(tmp_path / "missing.fit", "edge-530"):
            pytest.fail("must not yield")


def rebuild(messages, *, header_crc=False):
    from fit_tool.fit_file_header import FitFileHeader

    builder = FitFileBuilder()
    builder.add_all(messages)
    fit = builder.build()
    if header_crc:
        fit.header = FitFileHeader(records_size=fit.header.records_size, gen_crc=True)
        fit.crc = None
    return fit.to_bytes()


def test_nonzero_local_ids_big_endian_and_header_crc(tmp_path):
    from fit_tool.endian import Endian

    data_messages = messages(activity_bytes(developer=True))
    for index, message in enumerate(data_messages):
        message.local_id = index % 16
        message.endian = Endian.BIG
        message.definition_message = None
    original = rebuild(data_messages, header_crc=True)
    source = tmp_path / "big-endian.fit"
    source.write_bytes(original)
    with prepare_fit(source, "edge-840") as prepared:
        after = messages(prepared.read_bytes())
        for before, current in zip(data_messages, after):
            expected = values(before)
            if isinstance(before, FileIdMessage):
                expected["native", None, 1] = [1]
                expected["native", None, 2] = [4062]
            elif isinstance(before, DeviceInfoMessage) and before.device_index == 0:
                expected["native", None, 2] = [1]
                expected["native", None, 4] = [4062]
            assert values(current) == expected
    assert source.read_bytes() == original


def test_absent_recorder_fields_are_added_without_inventing_devices(tmp_path):
    data_messages = messages(activity_bytes(devices=False))
    identity = data_messages[0]
    identity.clear_field_by_id(1)
    identity.clear_field_by_id(2)
    creator = DeviceInfoMessage()
    creator.device_index = 0
    data_messages.append(creator)
    source = tmp_path / "minimal.fit"
    source.write_bytes(rebuild(data_messages))
    with prepare_fit(source, "edge-530") as prepared:
        after = messages(prepared.read_bytes())
        assert len(after) == len(data_messages)
        assert after[0].manufacturer == after[-1].manufacturer == 1
        assert after[0].product == after[-1].product == 3121
        assert after[-1].serial_number is None
        assert after[-1].software_version is None


def test_undescribed_developer_field_rejected_without_tempfile(tmp_path, monkeypatch):
    import garmincli.fit as module

    data_messages = messages(activity_bytes(developer=True))
    data_messages = [
        m for m in data_messages if m.global_id != 206
    ]  # field_description
    source = tmp_path / "undescribed.fit"
    source.write_bytes(rebuild(data_messages))
    created = []
    monkeypatch.setattr(module, "TemporaryDirectory", lambda **kw: created.append(kw))
    with pytest.raises(GarminCliError, match="unsupported"):
        with prepare_fit(source, "edge-530"):
            pytest.fail("must not yield")
    assert created == []


def test_temp_write_error_is_cli_error_and_cleans_directory(tmp_path, monkeypatch):
    from pathlib import Path

    source = tmp_path / "source.fit"
    source.write_bytes(activity_bytes())
    original_open = Path.open
    directories = []

    def fail_output(path, *args, **kwargs):
        if path.name == "upload.fit":
            directories.append(path.parent)
            raise OSError("synthetic disk failure")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fail_output)
    with pytest.raises(GarminCliError, match="temporary FIT"):
        with prepare_fit(source, "edge-530"):
            pytest.fail("must not yield")
    assert directories and not directories[0].exists()


def test_compressed_timestamp_input_fails_closed(tmp_path):
    from fit_tool.fit_file_header import FitFileHeader
    from fit_tool.utils.crc import crc16

    selected = messages(activity_bytes(devices=False))
    data = rebuild(selected[:3])  # file_id, event, first record
    parsed = FitFile.from_bytes(data)
    record = parsed.records[-1]
    timestamp = record.message.timestamp // 1000 - 631065600
    # A valid FIT compressed timestamp omits the first (timestamp) field bytes.
    compressed = bytes([0x80 | (timestamp & 31)]) + record.message.to_bytes()[4:]
    body = b"".join(r.to_bytes() for r in parsed.records[:-1]) + compressed
    payload = FitFileHeader(records_size=len(body)).to_bytes() + body
    source = tmp_path / "compressed.fit"
    source.write_bytes(payload + crc16(payload).to_bytes(2, "little"))
    with pytest.raises(GarminCliError, match="unsupported"):
        with prepare_fit(source, "edge-530"):
            pytest.fail("must not reinterpret compressed timestamps")


def test_rebuild_that_changes_measurements_is_rejected(tmp_path, monkeypatch):
    source = tmp_path / "source.fit"
    source.write_bytes(activity_bytes())
    original_build = FitFileBuilder.build

    def corrupt_build(builder):
        fit = original_build(builder)
        next(
            r.message for r in fit.records if isinstance(r.message, RecordMessage)
        ).power = 999
        return fit

    monkeypatch.setattr(FitFileBuilder, "build", corrupt_build)
    with pytest.raises(GarminCliError, match="unsupported"):
        with prepare_fit(source, "edge-530"):
            pytest.fail("must detect rebuild data loss")


@pytest.mark.parametrize(
    "case",
    ["declared-size", "field-base-type", "identity-type-array", "device-index-array"],
)
def test_malformed_envelope_or_ambiguous_field_encoding(tmp_path, case):
    from fit_tool.base_type import BaseType

    parsed = FitFile.from_bytes(activity_bytes())
    if case == "declared-size":
        parsed.header.records_size -= 1
    elif case == "field-base-type":
        identity = next(
            r.message for r in parsed.records if isinstance(r.message, FileIdMessage)
        )
        identity.definition_message.get_field_definition(3).base_type = BaseType.FLOAT32
    else:
        data_messages = [r.message for r in parsed.records if not r.is_definition]
        message = (
            data_messages[0] if case == "identity-type-array" else data_messages[1]
        )
        field = message.get_field_by_name(
            "type" if case == "identity-type-array" else "device_index"
        )
        field.growable = True
        field.set_encoded_value(1, 4)
        message.definition_message = None
        if case == "device-index-array":
            data_messages = data_messages[:2]
        parsed = FitFile.from_bytes(rebuild(data_messages))
    parsed.crc = None
    source = tmp_path / "ambiguous.fit"
    source.write_bytes(parsed.to_bytes())
    with pytest.raises(GarminCliError, match="FIT"):
        with prepare_fit(source, "edge-530"):
            pytest.fail("must reject malformed or ambiguous encoding")

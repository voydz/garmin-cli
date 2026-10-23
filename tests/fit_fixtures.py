"""Synthetic, nonpersonal FITs; no downloaded activity or account data."""

from fit_tool.base_type import BaseType
from fit_tool.data_message import DataMessage
from fit_tool.developer_field import DeveloperField
from fit_tool.field import Field
from fit_tool.fit_file_builder import FitFileBuilder
from fit_tool.profile.messages.developer_data_id_message import DeveloperDataIdMessage
from fit_tool.profile.messages.device_info_message import DeviceInfoMessage
from fit_tool.profile.messages.event_message import EventMessage
from fit_tool.profile.messages.field_description_message import FieldDescriptionMessage
from fit_tool.profile.messages.file_id_message import FileIdMessage
from fit_tool.profile.messages.lap_message import LapMessage
from fit_tool.profile.messages.record_message import RecordMessage
from fit_tool.profile.messages.session_message import SessionMessage
from fit_tool.profile.profile_type import FileType

TIME = 1700000000000


def activity_bytes(*, devices=True, developer=False, unknown=False, hr=False):
    identity = FileIdMessage()
    identity.type = FileType.ACTIVITY
    identity.manufacturer = 255
    identity.product = 99
    identity.serial_number = 123456
    identity.time_created = TIME
    messages = [identity]
    if devices:
        for index in (0, 1, 2):
            device = DeviceInfoMessage()
            device.device_index = index
            device.manufacturer = 255 if index == 0 else 32
            device.product = 99 + index
            device.serial_number = 123456 + index
            device.software_version = 1.23
            device.timestamp = TIME
            messages.append(device)
    if developer:
        application = DeveloperDataIdMessage()
        application.developer_data_index = 0
        application.application_id = list(range(16))
        description = FieldDescriptionMessage()
        description.developer_data_index = 0
        description.field_definition_number = 0
        description.fit_base_type_id = BaseType.UINT16.value
        description.field_name = "synthetic_power"
        description.units = "watts"
        description.scale = 1
        description.offset = 0
        messages.extend([application, description])
    event = EventMessage()
    event.timestamp = TIME
    event.event = 0
    event.event_type = 0
    messages.append(event)
    for index in range(3):
        record = RecordMessage()
        record.timestamp = TIME + index * 1000
        record.power = 200 + index
        record.cadence = 85 + index
        record.distance = 5.5 * index
        record.speed = 5.5
        if hr:
            record.heart_rate = 120 + index
        if developer:
            field = DeveloperField(
                field_id=0,
                developer_data_index=0,
                name="synthetic_power",
                base_type=BaseType.UINT16,
                size=2,
            )
            field.set_value(0, 777 + index)
            record.developer_fields.append(field)
        messages.append(record)
    for cls in (LapMessage, SessionMessage):
        message = cls()
        message.timestamp = TIME + 2000
        message.start_time = TIME
        message.total_elapsed_time = 2.0
        message.total_timer_time = 2.0
        message.total_distance = 11.0
        messages.append(message)
    if unknown:
        message = DataMessage(global_id=65000)
        field = Field(field_id=42, base_type=BaseType.UINT16, size=2)
        field.set_value(0, 1234)
        message.fields.append(field)
        messages.append(message)
    builder = FitFileBuilder(auto_define=True)
    builder.add_all(messages)
    return builder.build().to_bytes()

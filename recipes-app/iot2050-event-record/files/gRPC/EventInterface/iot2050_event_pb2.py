# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: gRPC/EventInterface/iot2050-event.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\'gRPC/EventInterface/iot2050-event.proto\x12\x0b\x65ventrecord\"1\n\x0cWriteRequest\x12\x12\n\nevent_type\x18\x01 \x01(\t\x12\r\n\x05\x65vent\x18\x02 \x01(\t\"-\n\nWriteReply\x12\x0e\n\x06status\x18\x01 \x01(\x05\x12\x0f\n\x07message\x18\x02 \x01(\t\"!\n\x0bReadRequest\x12\x12\n\nevent_type\x18\x01 \x01(\t\";\n\tReadReply\x12\x0e\n\x06status\x18\x01 \x01(\x05\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\r\n\x05\x65vent\x18\x03 \x01(\t2\x88\x01\n\x0b\x45ventRecord\x12=\n\x05Write\x12\x19.eventrecord.WriteRequest\x1a\x17.eventrecord.WriteReply\"\x00\x12:\n\x04Read\x12\x18.eventrecord.ReadRequest\x1a\x16.eventrecord.ReadReply\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'gRPC.EventInterface.iot2050_event_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_WRITEREQUEST']._serialized_start=56
  _globals['_WRITEREQUEST']._serialized_end=105
  _globals['_WRITEREPLY']._serialized_start=107
  _globals['_WRITEREPLY']._serialized_end=152
  _globals['_READREQUEST']._serialized_start=154
  _globals['_READREQUEST']._serialized_end=187
  _globals['_READREPLY']._serialized_start=189
  _globals['_READREPLY']._serialized_end=248
  _globals['_EVENTRECORD']._serialized_start=251
  _globals['_EVENTRECORD']._serialized_end=387
# @@protoc_insertion_point(module_scope)

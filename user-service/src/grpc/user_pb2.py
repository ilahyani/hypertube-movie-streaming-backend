# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: user.proto
# Protobuf Python Version: 5.27.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    2,
    '',
    'user.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nuser.proto\x12\x04user\"k\n\x04User\x12\n\n\x02id\x18\x01 \x01(\t\x12\r\n\x05\x65mail\x18\x02 \x01(\t\x12\x10\n\x08username\x18\x03 \x01(\t\x12\x12\n\nfirst_name\x18\x04 \x01(\t\x12\x11\n\tlast_name\x18\x05 \x01(\t\x12\x0f\n\x07picture\x18\x06 \x01(\t\"\x1c\n\x0egetUserRequest\x12\n\n\x02id\x18\x01 \x01(\t\"+\n\x0fgetUserResponse\x12\x18\n\x04user\x18\x01 \x01(\x0b\x32\n.user.User2H\n\x07getUser\x12=\n\x0egetUserService\x12\x14.user.getUserRequest\x1a\x15.user.getUserResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'user_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_USER']._serialized_start=20
  _globals['_USER']._serialized_end=127
  _globals['_GETUSERREQUEST']._serialized_start=129
  _globals['_GETUSERREQUEST']._serialized_end=157
  _globals['_GETUSERRESPONSE']._serialized_start=159
  _globals['_GETUSERRESPONSE']._serialized_end=202
  _globals['_GETUSER']._serialized_start=204
  _globals['_GETUSER']._serialized_end=276
# @@protoc_insertion_point(module_scope)

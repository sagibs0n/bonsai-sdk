# Copyright (C) 2018 Bonsai, Inc.

import uuid
import os

# protobuf
from google.protobuf.descriptor_pb2 import FileDescriptorProto
from google.protobuf.message_factory import MessageFactory
from google.protobuf.json_format import MessageToJson

# bonsai
from bonsai_ai.proto import inkling_types_pb2


class InklingMessageFactory(object):
    def __init__(self):
        self._message_factory = MessageFactory()
        inkling_file_desc = FileDescriptorProto()
        inkling_types_pb2.DESCRIPTOR.CopyToProto(inkling_file_desc)
        self._message_factory.pool.Add(inkling_file_desc)

    def message_for_dynamic_message(self, dynamic_msg, desc_proto):
        if desc_proto is None:
            return None
        message = self.new_message_from_proto(desc_proto)
        message.ParseFromString(dynamic_msg)
        return message

    def new_message_from_proto(self, desc_proto):
        # TODO(oren.leiman): in sdk1, this happens once for each
        # DescriptorProto. Profile and consider refactoring.
        package = self._create_package_name(desc_proto)
        desc = self._find_descriptor(desc_proto, package)
        if desc is None:
            raise Exception(
                "new_message_from_proto: unable to find descriptor")

        message_cls = self._message_factory.GetPrototype(desc)
        if message_cls is None:
            raise Exception(
                "new_message_from_proto: unable to get prototype")

        return message_cls()

    def _create_package_name(self, desc_proto):
        if not desc_proto.name:
            desc_proto.name = '__INTERNAL_ANONYMOUS__'
        desc_proto_str = MessageToJson(desc_proto)
        signature = hash(desc_proto_str)
        return 'p{}'.format(signature).replace('-', '_')

    def _find_descriptor(self, desc_proto, package):
        if desc_proto is None:
            return None
        full_name = '{}.{}'.format(package, desc_proto.name)
        pool = self._message_factory.pool
        try:
            return pool.FindMessageTypeByName(full_name)
        except KeyError:
            pass

        proto_name = str(uuid.uuid4())
        proto_path = os.path.join(package, proto_name + '.proto')
        file_desc_proto = FileDescriptorProto()
        file_desc_proto.message_type.add().MergeFrom(desc_proto)
        file_desc_proto.name = proto_path
        file_desc_proto.package = package

        file_desc_proto.dependency.append('bonsai/proto/inkling_types.proto')

        file_desc_proto.public_dependency.append(0)

        pool.Add(file_desc_proto)
        result = pool.FindFileByName(proto_path)
        return result.message_types_by_name[desc_proto.name]

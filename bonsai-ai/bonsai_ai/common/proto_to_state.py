# Copyright (C) 2018 Bonsai, Inc.


def dict_for_message(message):
    """
    Unpack a protobuf message into a Python dictionary
    :return: dictionary
    """
    result = {}
    # If the message is bogus, return an empty dictionary rather
    # than crashing.
    if message is not None:
        for field in message.DESCRIPTOR.fields:
            result[field.name] = getattr(message, field.name)
    return result

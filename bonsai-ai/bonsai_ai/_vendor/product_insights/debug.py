import traceback


# noinspection PyUnreachableCode
def handle_internal_exception(exception):
    # type: (Exception) -> None
    return  # When debugging, commenting out this line makes internal exceptions loud

    traceback.print_exc()

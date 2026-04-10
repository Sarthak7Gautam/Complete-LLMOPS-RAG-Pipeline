from multi_doc_chat.exceptions import custom_exception

try:
    1/0
except ZeroDivisionError as e:
    raise custom_exception.DocumentPortalException('Math failed',e)
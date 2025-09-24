from fastapi import APIRouter

from pets.api.test.schema import TestMessage

router = APIRouter()


@router.post("/", response_model=TestMessage)
async def send_test_message(
    incoming_message: TestMessage,
) -> TestMessage:
    """
    Sends test message back to user for template demonstration.

    :param incoming_message: incoming test message.
    :returns: message same as the incoming (for testing purposes).
    """
    return incoming_message

import os
import time
import logging

from kittycad.api.ml import create_text_to_cad, get_text_to_cad_model_for_user
from kittycad.client import ClientFromEnv
from kittycad.models import (
    ApiCallStatus,
    Error,
    FileExportFormat,
    TextToCad,
    TextToCadCreateBody,
)

logger = logging.getLogger(__name__)

BINARY_FORMAT = {FileExportFormat.GLB}


def text_to_cad(
    prompt: str,
    output_file_name: str = "tmp",
    output_format: str = "glb",
):
    # Convert a string literal to the enum value.
    try:
        output_format = FileExportFormat(output_format.lower())
    except ValueError as e:
        logger.exception(f"Error: Invalid format string: {e}")
        return None
    output_file_name = f"{output_file_name}.{output_format}"

    # Create our client.
    client = ClientFromEnv()

    logger.info(
        f"New Text-to-CAD job:\nPrompt: {prompt}\nOutput format: {output_format}\nOutput file name: {output_file_name}"
    )

    # Prompt the API to generate a 3D model from text.
    response = create_text_to_cad.sync(
        client=client,
        output_format=output_format,
        body=TextToCadCreateBody(
            prompt=prompt,
        ),
    )

    if isinstance(response, Error) or response is None:
        logger.error(f"Text-to-CAD failed: {response}")
        return None

    result: TextToCad = response

    # Polling to check if the task is complete
    while result.completed_at is None:
        # Wait for 5 seconds before checking again
        time.sleep(5)

        # Check the status of the task
        response = get_text_to_cad_model_for_user.sync(
            client=client,
            id=result.id,
        )

        if isinstance(response, Error) or response is None:
            logger.error(f"Text-to-CAD failed: {response}")
            return None

        result = response

    if result.status == ApiCallStatus.FAILED:
        # Print out the error message
        logger.error(f"Text-to-CAD failed: {result.error}")
        return None

    elif result.status == ApiCallStatus.COMPLETED:
        if result.outputs is None:
            logger.error("Text-to-CAD completed but returned no files.")
            return None

        # Print out the names of the generated files
        logger.info(f"Text-to-CAD completed and returned {len(result.outputs)} files:")
        for name in result.outputs:
            logger.info(f"  * {name}")

        source_file_name = f"source.{output_format}"
        if source_file_name not in result.outputs:
            logger.error(
                f"Desired format {output_format} is not in the generated files."
            )
            return None

        # Save the generated data to desired format
        final_result = result.outputs[source_file_name]
        if output_format in BINARY_FORMAT:
            with open(output_file_name, "wb") as output_file:
                output_file.write(final_result)
        else:
            with open(output_file_name, "w", encoding="utf-8") as output_file:
                output_file.write(final_result.decode("utf-8"))
        logger.info(f"Saved output to {output_file.name}")
        return os.path.join(os.getcwd(), output_file_name)
    else:
        logger.error(f"Unknown API status {result.status}")

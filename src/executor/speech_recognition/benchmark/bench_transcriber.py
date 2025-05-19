import os
import sys
import argparse
import json
import logging

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from src.transcriber import WhisperS2tTranscriber


def main():
    """
    Creates a command-line interface for the `transcribe` function.
    """
    parser = argparse.ArgumentParser(description="Transcribe audio files.")

    parser.add_argument(
        "audio_file",
        type=str,
        help="Audio file to transcribe.",
    )
    parser.add_argument(
        "-n",
        type=int,
        default=1,
        help="Iteration of benchmark.",
    )
    parser.add_argument("--model_name", type=str, default="base", help="Name of the transcription model.")
    parser.add_argument(
        "--model_backend",
        type=str,
        default="CTranslate2",
        help="Backend for the transcription model (default: CTranslate2).",
    )
    parser.add_argument(
        "--model_params",
        type=str,
        help="JSON string representing model parameters (optional).",
    )
    
    parser.add_argument("--lang", type=str, default="en", help="Language to transcribe.")
    parser.add_argument(
        "--prompt",
        type=str,
        default=None,
        help="Initial prompt for the transcription model (optional).",
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=24,
        help="Batch size for transcription (default: 24).",
    )
    parser.add_argument(
        "--transcribe_kwargs",
        type=str,
        help="JSON string representing keyword arguments to pass to transcribe (optional).",
    )

    args = parser.parse_args()

    # Prepare arguments for the transcribe function
    model_params = {}
    if args.model_params:
        try:
            model_params = json.loads(args.model_params)
        except json.JSONDecodeError as e:
            print(f"Error decoding model_params JSON: {e}")
            return

    transcribe_kwargs = {}
    if args.transcribe_kwargs:
        try:
            transcribe_kwargs = json.loads(args.transcribe_kwargs)
        except json.JSONDecodeError as e:
            print(f"Error decoding transcribe_kwargs JSON: {e}")
            return

    # Call the transcribe function
    try:
        for _ in range(args.n):
            transcriber = WhisperS2tTranscriber()
            transcriber.transcribe(
                model_name=args.model_name,
                model_backend=args.model_backend,
                model_params=model_params,
                audio_files=[args.audio_file],
                lang_codes=[args.lang],
                tasks=["transcribe"],
                initial_prompts=[args.prompt],
                batch_size=args.batch_size,
                **transcribe_kwargs,
            )
            print("Transcription completed successfully.")
            del transcriber
    except Exception as e:
        print(f"An error occurred during transcription: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
    main()

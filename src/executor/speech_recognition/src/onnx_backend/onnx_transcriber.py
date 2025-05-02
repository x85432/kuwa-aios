# ---------------------------------------------------------------------
# Copyright (c) 2024 Qualcomm Innovation Center, Inc. All rights reserved.
# Copyright (c) 2025 Yung-Hsiang Hu. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# ---------------------------------------------------------------------
import onnxruntime
import argparse
import time
import logging
import functools
import numpy as np
from datetime import datetime
import os, sys

from qai_hub_models.models._shared.whisper.app import WhisperApp

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.onnx_backend.model import WhisperBaseONNX


def load_audio_file(filepath: str) -> tuple[np.array, int]:
    import audio2numpy as a2n  # import here, as this requires ffmpeg to be installed on host machine

    audio, audio_sample_rate = a2n.audio_from_file(filepath)
    audio = np.mean(audio, axis=1)

    return audio, audio_sample_rate


logger = logging.getLogger(__name__)


class OnnxTranscriber:
    """
    Encapsulation of WhisperS2T process for multi-processing.
    """

    def __init__(self, encoder_path, decoder_path):
        self.encoder_path = encoder_path
        self.decoder_path = decoder_path
        self.load_model()

    @functools.lru_cache
    def load_model(self, **model_params):
        if self.encoder_path is None or self.decoder_path is None:
            return None

        logger.debug(
            f"Available Execution Providers: {onnxruntime.get_available_providers()}"
        )
        logger.debug(f"Parameters to load model: {model_params}")
        # Load whisper model
        logger.debug("Loading model...")
        start_time = time.time()
        whisper = WhisperApp(WhisperBaseONNX(self.encoder_path, self.decoder_path))
        end_time = time.time()
        logger.debug(f"Model {self.encoder_path}; {self.decoder_path} loaded")
        logger.debug(f"Model loading time: {end_time - start_time:.4f}")
        return whisper

    def transcribe(
        self,
        model_name: str,
        model_backend: str = "ONNX",
        model_params: dict = None,
        audio_files: list = [],
        **transcribe_kwargs,
    ):
        logger.debug("Transcribing...")
        result = None
        try:
            model = self.load_model()
            audio, audio_sample_rate = load_audio_file(audio_files[0])
            start_time = time.time()
            text = model.transcribe(audio, audio_sample_rate)
            end_time = time.time()

            result = {
                "start_time": 0,  # [TODO] Timestamp
                "end_time": 0,
                "text": text,
            }

        except Exception:
            logger.exception("Error when generating transcription")
            raise

        logger.debug("Done transcribing.")
        logger.debug(f"Transcribing time: {end_time - start_time:.4f}")
        return [[result]]

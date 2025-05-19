# ---------------------------------------------------------------------
# Copyright (c) 2024 Qualcomm Innovation Center, Inc. All rights reserved.
# Copyright (c) 2025 Yung-Hsiang Hu. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# ---------------------------------------------------------------------
import os
import sys
import re
import onnxruntime
import argparse
import time
import logging
import functools
import numpy as np
from datetime import datetime
from pathlib import Path
from huggingface_hub import hf_hub_download

from qai_hub_models.models._shared.whisper.app import WhisperApp
from qai_hub_models.utils.executable_onnx_model import ExecutableOnnxModel

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger(__name__)

def parse_model_path(model_path):
    if os.path.isfile(model_path):
        return Path(model_path).resolve()
    regex = r"hf://([^?]+)\?(.*)"
    match = re.match(regex, model_path)
    if not match:
        raise Exception(f"Invalid model_path format: {model_path}")

    repo_id = match.group(1)
    filename = match.group(2)
    model_path = hf_hub_download(repo_id=repo_id, filename=filename)
    logger.debug(f"Downloaded model from HF. Path: {model_path}")

    return Path(model_path).resolve()

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
        logger.debug(f"Encoder path: {parse_model_path(self.encoder_path)}")
        logger.debug(f"Decoder path: {parse_model_path(self.decoder_path)}")
        whisper = WhisperApp(
            ExecutableOnnxModel.OnNPU(self.encoder_path),
            ExecutableOnnxModel.OnNPU(self.decoder_path),
            num_decoder_blocks=6,
            num_decoder_heads=8,
            attention_dim=512,
            mean_decode_len=224,
        )
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
            start_time = time.time()
            text = model.transcribe(audio_files[0])
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

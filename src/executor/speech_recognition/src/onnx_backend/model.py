# ---------------------------------------------------------------------
# Copyright (c) 2024 Qualcomm Innovation Center, Inc. All rights reserved.
# Copyright (c) 2025 Yung-Hsiang Hu. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# ---------------------------------------------------------------------
import numpy as np
import onnxruntime
import logging
from qai_hub_models.models._shared.whisper.model import (
    Whisper,
    N_MELS,
    MELS_AUDIO_LEN,
    MEAN_DECODE_LEN,
    AUDIO_EMB_LEN,
)
from qai_hub_models.utils.base_model import (
    BasePrecompiledModel,
)
from qai_hub_models.utils.input_spec import InputSpec

logger = logging.getLogger(__name__)

def get_onnxruntime_session_with_qnn_ep(path):
    options = onnxruntime.SessionOptions()
    # options.log_severity_level = 0  # Verbose
    options.add_session_config_entry("session.disable_cpu_ep_fallback", "1")
    session = onnxruntime.InferenceSession(
        path,
        sess_options=options,
        # providers=["CPUExecutionProvider"],
        providers=["QNNExecutionProvider"],
        provider_options=[
            {
                "backend_path": "QnnHtp.dll",
                "htp_performance_mode": "burst",
                "high_power_saver": "sustained_high_performance",
                "enable_htp_fp16_precision": "1",
                "htp_graph_finalization_optimization_mode": "3",
                "soc_model": 60,
                "htp_arch": 73,
            }
        ],
    )
    logger.info(f"Using {session.get_providers()}")
    return session


class ONNXEncoderWrapper(BasePrecompiledModel):
    def __init__(self, encoder_path):
        super().__init__(encoder_path)
        self.session = get_onnxruntime_session_with_qnn_ep(encoder_path)

    def to(self, *args):
        return self

    def __call__(self, audio):
        return self.session.run(None, {"audio": audio})

    @staticmethod
    def get_input_spec() -> InputSpec:
        """
        Returns the input specification (name -> (shape, type). This can be
        used to submit profiling job on Qualcomm AI Hub.
        """
        return dict(audio=((1, N_MELS, MELS_AUDIO_LEN), "float32"))

    @staticmethod
    def get_output_names() -> list[str]:
        return ["k_cache", "v_cache"]

    @classmethod
    def from_precompiled(cls):
        return cls("WhisperEncoderInf.onnx")


class ONNXDecoderWrapper(BasePrecompiledModel):
    def __init__(self, decoder_path):
        super().__init__(decoder_path)
        self.session = get_onnxruntime_session_with_qnn_ep(decoder_path)

    def to(self, *args):
        return self

    def __call__(
        self, x, index, k_cache_cross, v_cache_cross, k_cache_self, v_cache_self
    ):
        return self.session.run(
            None,
            {
                "x": x.astype(np.int32),
                "index": np.array(index),
                "k_cache_cross": k_cache_cross,
                "v_cache_cross": v_cache_cross,
                "k_cache_self": k_cache_self,
                "v_cache_self": v_cache_self,
            },
        )

    @staticmethod
    def get_input_spec(
        num_blocks: int, attention_dim: int, num_heads: int
    ) -> InputSpec:
        """
        Returns the input specification (name -> (shape, type). This can be
        used to submit profiling job on Qualcomm AI Hub.
        """
        specs: InputSpec = dict(
            x=((1, 1), "int32"),
            index=((1, 1), "int32"),
            k_cache_cross=(
                (num_blocks, num_heads, attention_dim // num_heads, AUDIO_EMB_LEN),
                "float32",
            ),
            v_cache_cross=(
                (num_blocks, num_heads, AUDIO_EMB_LEN, attention_dim // num_heads),
                "float32",
            ),
            k_cache_self=(
                (num_blocks, num_heads, attention_dim // num_heads, MEAN_DECODE_LEN),
                "float32",
            ),
            v_cache_self=(
                (num_blocks, num_heads, MEAN_DECODE_LEN, attention_dim // num_heads),
                "float32",
            ),
        )

        return specs

    @staticmethod
    def get_output_names() -> list[str]:
        return ["logits", "k_cache", "v_cache"]

    @classmethod
    def from_precompiled(cls):
        return cls("WhisperDecoderInf.onnx")


class WhisperBaseONNX(Whisper):
    def __init__(self, encoder_path, decoder_path):
        return super().__init__(
            ONNXEncoderWrapper(encoder_path),
            ONNXDecoderWrapper(decoder_path),
            num_decoder_blocks=6,
            num_heads=8,
            attention_dim=512,
        )

import os
import logging
import torch
import whisper_s2t
import functools
from whisper_s2t.backends.ctranslate2.hf_utils import download_model as whisper_s2t_download_model
from huggingface_hub.constants import HUGGINGFACE_HUB_CACHE

logger = logging.getLogger(__name__)

class WhisperS2tTranscriber:
    """
    Encapsulation of WhisperS2T process for multi-processing.
    """

    def __init__(self):
        pass

    @functools.lru_cache
    def load_model(
        self,
        name = None,
        enable_word_ts:bool = False,
        **model_params
    ):
        if name is None: return None
        if os.path.isdir(name):
            model_path = name
        else:
            model_path = whisper_s2t_download_model(
                name,
                cache_dir=HUGGINGFACE_HUB_CACHE,
            )
        
        device_index = os.environ.get("CUDA_VISIBLE_DEVICES", "").split(',')
        device_index = [int(i) for i in device_index if i.isdecimal()]

        # "word_timestamps" needs configuring when loading model.
        model_params.update({"asr_options":{"word_timestamps": True}} if enable_word_ts else {})
        model_params.update(dict(
            model_identifier=model_path,
            device_index=device_index,
        ))

        logger.debug(f"Parameters to load model: {model_params}")
        model = whisper_s2t.load_model(**model_params)
        logger.debug(f"Model {name} loaded")
        return model
    
    def transcribe(
        self,
        model_name:str,
        model_backend:str="CTranslate2",
        model_params:dict=None,
        audio_files:list=[],
        **transcribe_kwargs
    ):
        logger.debug("Transcribing...")
        result = None
        try:
            default_device, default_compute_type = ("cpu", "int8")
            if torch.cuda.is_available():
                default_device, default_compute_type = ("cuda", "float16")
            device = model_params.pop("device", default_device)
            compute_type = model_params.pop("compute_type", default_compute_type)
            logger.info(f"Using device {device}. And compute type {compute_type}")
            model = self.load_model(
                name=model_name,
                enable_word_ts=model_params.get("word_timestamps", False),
                # ---Transparent kwargs---
                backend=model_backend,
                device=device,
                compute_type=compute_type,
            )
            if model_params is not None and len(model_params) > 0:
                model.update_params({'asr_options': model_params})
            result = model.transcribe_with_vad(audio_files, **transcribe_kwargs)

        except Exception:
            logger.exception("Error when generating transcription")
            raise

        logger.debug("Done transcribe.")
        return result
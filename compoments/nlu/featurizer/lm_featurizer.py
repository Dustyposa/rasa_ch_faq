import logging
from functools import partial
from pathlib import Path
from typing import List

import numpy as np

from rasa.nlu.featurizers.dense_featurizer.lm_featurizer import LanguageModelFeaturizer

logger = logging.getLogger(__name__)


class OnnxLanguageModelFeaturizer(LanguageModelFeaturizer):
    defaults = {
        # name of the language model to load.
        "model_name": "bert",
        # Pre-Trained weights to be loaded(string)
        "model_weights": None,
        # an optional path to a specific directory to download
        # and cache the pre-trained model weights.
        "cache_dir": None,
        "onnx": True,
        "quantize": True,
        "opset": 12,
        "output_dir": "onnx_model"
    }

    def _load_model_instance(self, skip_model_load: bool) -> None:
        """Try loading the model instance.

        Args:
            skip_model_load: Skip loading the model instances to save time. This
            should be True only for pytests
        """
        if skip_model_load:
            # This should be True only during pytests
            return

        from rasa.nlu.utils.hugging_face.registry import (
            model_class_dict,
            model_tokenizer_dict,
        )

        logger.debug(f"Loading Tokenizer and Model for {self.model_name}")

        self.tokenizer = model_tokenizer_dict[self.model_name].from_pretrained(
            self.model_weights, cache_dir=self.cache_dir
        )
        output_path = Path(self.component_config['output_dir'])
        if self.component_config["onnx"]:
            from transformers import convert_graph_to_onnx

            onnx_path = old_onnx_path = (output_path / f"{self.model_name}.onnx").absolute()
            if self.is_clean_dir(output_path) or not onnx_path.exists():
                # onnx 转化
                logger.info("进行 onnx 转化")
                from transformers import convert_graph_to_onnx
                convert_graph_to_onnx.convert(
                    framework="pt",  # tf 暂时有问题, 转化后无法使用
                    model=self.model_weights,
                    output=onnx_path,
                    tokenizer=self.tokenizer,
                    opset=self.defaults["opset"]
                )

            if self.component_config["quantize"]:
                logger.info("进行量化")
                onnx_path = onnx_path.with_name("-optimized-quantized.".join(onnx_path.name.split(".")))
                if not onnx_path.exists():
                    # 开启量化
                    optimize_path = convert_graph_to_onnx.optimize(old_onnx_path)
                    onnx_path = convert_graph_to_onnx.quantize(optimize_path)
                    Path(optimize_path).unlink()
            logger.info("加载onnx模型")
            self.model = self.load_onnx_model(onnx_path)
            self.input_convert_func = lambda x: np.array(x, dtype="i8")
            self.mode_run = lambda x: partial(self.model.run, None)(x)
            self.get_feature = lambda x: x[0]
            self._create_model_input = self._create_model_input_for_pt_onnx

        else:
            logger.info("加载非onnx模型")
            self.model = model_class_dict[self.model_name].from_pretrained(
                self.model_weights, cache_dir=self.cache_dir
            )
            self.input_convert_func = lambda x: np.array(x)
            self.mode_run = self.model
            self.get_feature = lambda x: x[0].numpy()
            self._create_model_input = self._create_model_input_for_normal

        # Use a universal pad token since all transformer architectures do not have a
        # consistent token. Instead of pad_token_id we use unk_token_id because
        # pad_token_id is not set for all architectures. We can't add a new token as
        # well since vocabulary resizing is not yet supported for TF classes.
        # Also, this does not hurt the model predictions since we use an attention mask
        # while feeding input.
        self.pad_token_id = self.tokenizer.unk_token_id

    def _compute_batch_sequence_features(
            self, batch_attention_mask: np.ndarray, padded_token_ids: List[List[int]]
    ) -> np.ndarray:
        """Feed the padded batch to the language model.

        Args:
            batch_attention_mask: Mask of 0s and 1s which indicate whether the token
            is a padding token or not.
            padded_token_ids: Batch of token ids for each example. The batch is padded
            and hence can be fed at once.

        Returns:
            Sequence level representations from the language model.
        """
        inputs = self._create_model_input(batch_attention_mask, padded_token_ids)
        model_outputs = self.mode_run(
            inputs
        )
        # sequence hidden states is always the first output from all models
        sequence_hidden_states = self.get_feature(model_outputs)

        return sequence_hidden_states

    @staticmethod
    def load_onnx_model(path: Path):
        from os import environ
        from psutil import cpu_count

        from onnxruntime import ExecutionMode, InferenceSession, SessionOptions

        # Constants from the performance optimization available in onnxruntime
        # It needs to be done before importing onnxruntime
        environ["OMP_NUM_THREADS"] = str(cpu_count(logical=True))
        environ["OMP_WAIT_POLICY"] = 'ACTIVE'

        options = SessionOptions()
        options.intra_op_num_threads = 1
        options.execution_mode = ExecutionMode.ORT_SEQUENTIAL
        session = InferenceSession(str(path.absolute()), options)
        return session

    @staticmethod
    def is_clean_dir(path: Path) -> bool:
        return not path.exists() or next(path.iterdir(), None) is None

    def _create_model_input_for_pt_onnx(self, batch_attention_mask: np.ndarray, padded_token_ids: List[List[int]]):
        row, column = batch_attention_mask.shape
        return {
            "input_ids": self.input_convert_func(padded_token_ids),
            "attention_mask": self.input_convert_func(batch_attention_mask),
            "token_type_ids": self.input_convert_func(
                np.zeros((row, column)))
        }

    def _create_model_input_for_normal(self, batch_attention_mask: np.ndarray, padded_token_ids: List[List[int]]):
        return {
            "input_ids": self.input_convert_func(padded_token_ids),
            "attention_mask": self.input_convert_func(batch_attention_mask),
        }

from rasa.nlu.featurizers.dense_featurizer.lm_featurizer import LanguageModelFeaturizer
from rasa_sdk import logger
from transformers import BertTokenizer, TFAlbertModel


class AlbertFeaturizer(LanguageModelFeaturizer):
    """
    模型下载参考地址:
    https://huggingface.co/voidful/albert_chinese_large/tree/main
    """

    def _load_model_instance(self, skip_model_load: bool) -> None:
        """Try loading the model instance.

        Args:
            skip_model_load: Skip loading the model instances to save time. This
            should be True only for pytests
        """
        if skip_model_load:
            # This should be True only during pytests
            return

        logger.debug(f"Loading Tokenizer and Model for {self.model_name}")

        self.tokenizer = BertTokenizer.from_pretrained(
            "voidful/albert_chinese_large", cache_dir=self.cache_dir
        )
        self.model = TFAlbertModel.from_pretrained(
            self.model_weights, cache_dir=self.cache_dir, from_pt=True
        )

        # Use a universal pad token since all transformer architectures do not have a
        # consistent token. Instead of pad_token_id we use unk_token_id because
        # pad_token_id is not set for all architectures. We can't add a new token as
        # well since vocabulary resizing is not yet supported for TF classes.
        # Also, this does not hurt the model predictions since we use an attention mask
        # while feeding input.
        self.pad_token_id = self.tokenizer.unk_token_id

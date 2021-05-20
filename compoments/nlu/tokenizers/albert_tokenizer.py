from typing import Dict, Any, Text

from transformers import BertTokenizerFast

from compoments.nlu.tokenizers.bert_tokenizer import CustomBertTokenizer


class CustomAlbertTokenizer(CustomBertTokenizer):
    defaults = {
        "model_weights": "voidful/albert_chinese_large",
        "cache_dir": "./tmp"
    }

    def __init__(self, component_config: Dict[Text, Any] = None) -> None:
        super(CustomBertTokenizer, self).__init__(component_config)
        self.tokenizer = BertTokenizerFast.from_pretrained(
            self.component_config["model_weights"], cache_dir=self.component_config.get("cache_dir"), use_fast=True
        )

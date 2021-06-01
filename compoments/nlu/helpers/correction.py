from typing import List, Text, Dict, Optional, Any, Tuple

from rasa.nlu.components import Component
from rasa.shared.nlu.constants import TEXT as R_TEXT
from rasa.shared.nlu.training_data.message import Message


class TextCorrection(Component):
    defaults = {
        "model_dir": "./pre_models/xmnlp-models",  # 模型地址
        "threshold": 1.0  # 判定阈值
    }
    OLD_TEXT_KEY = "old_text"

    def __init__(self, component_config: Optional[Dict[Text, Any]] = None) -> None:
        super(TextCorrection, self).__init__(component_config)

        self.model = self._load_model()

    @classmethod
    def required_packages(cls) -> List[Text]:
        return ["xmnlp"]

    def _load_model(self):
        import xmnlp
        xmnlp.set_model(self.component_config['model_dir'])
        return xmnlp

    def process(self, message: Message, **kwargs: Any) -> None:
        if message.get(R_TEXT):
            have_error, result = self.check_text(message.get(R_TEXT))
            if have_error:
                new_t, old_t = result
                message.set(R_TEXT, new_t)
                message.set(self.OLD_TEXT_KEY, old_t)

    def check_text(self, text: str) -> Tuple[bool, Tuple[str, str]]:
        replace_result = {}
        threshold = self.component_config["threshold"]
        for pair, result in self.model.checker(text, k=1).items():
            if result[0][-1] >= threshold:
                replace_result[pair[0]] = result[0][0]
        if replace_result:
            old_text = text
            tmp = list(text)
            for i, v in replace_result.items():
                tmp[i] = v
            new_text = "".join(tmp)
            return True, (new_text, old_text)
        return False, ("", "")

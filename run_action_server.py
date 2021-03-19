from rasa.shared.constants import DEFAULT_ACTIONS_PATH
from rasa_sdk.endpoint import run

run(
    action_package_name=DEFAULT_ACTIONS_PATH,
    port=8080
)

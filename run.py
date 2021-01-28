import rasa

from channels.channel import CustomInput

rasa.run(
    model="models",
    endpoints="endpoints.yml",
    # connector="channels.channel.CustomInput"
    credentials="credentials.yml"
)

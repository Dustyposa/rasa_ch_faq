import rasa

rasa.run(
    model="models",
    endpoints="endpoints.yml",
    credentials="credentials.yml"
)

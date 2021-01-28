import rasa

rasa.train(
    domain="domain.yml",
    config="config.yml",
    training_files="data",
)


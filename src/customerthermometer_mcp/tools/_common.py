from .._json import error_envelope

NO_TOKEN = error_envelope(
    "not_configured",
    "No Customer Thermometer credentials. Send the X-CustomerThermometer-Api-Key "
    "and X-CustomerThermometer-Api-Url headers.",
    False,
)

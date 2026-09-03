import importlib


def test_compliance_model_is_registered():
    models = importlib.import_module("app.models")

    assert hasattr(models, "Compliance")

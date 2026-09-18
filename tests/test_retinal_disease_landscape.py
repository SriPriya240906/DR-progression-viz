from backend.disease_landscape import build_disease_landscape


def test_landscape_is_deterministic_and_only_dr_is_supported():
    first = build_disease_landscape()
    second = build_disease_landscape()

    assert first == second
    assert first["available"] is True
    assert first["landscape_type"] == "capability_map"
    assert not any("score" in key.lower() or "probability" in key.lower() for key in first)
    supported = [item for item in first["diseases"] if item["status"] == "supported"]
    assert [item["name"] for item in supported] == ["Diabetic Retinopathy"]
    assert supported[0]["prediction_available"] is True
    assert supported[0]["labels"] == [
        "No Diabetic Retinopathy",
        "Mild",
        "Moderate",
        "Severe",
        "Proliferative DR",
    ]


def test_investigated_additional_diseases_are_explicitly_unavailable():
    landscape = build_disease_landscape()
    names = {item["name"] for item in landscape["diseases"]}
    for expected in {"Glaucoma", "Age-related Macular Degeneration", "Diabetic Macular Edema", "Cataract", "Retinal Vein Occlusion"}:
        assert expected in names
    for item in landscape["diseases"]:
        if item["name"] != "Diabetic Retinopathy":
            assert item["status"] == "unavailable"
            assert item["prediction_available"] is False
            assert item["model_available"] is False
            assert item["labels"] == []

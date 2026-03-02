from scripts.generate_frontend_types import TypeConverter


def test_convert_union_tuple_style_list_annotations() -> None:
    result = TypeConverter.convert_type("Union[(List[float], List[List[float]])]")
    assert result == "number[] | number[][]"


def test_convert_optional_dict_tuple_style_annotations() -> None:
    result = TypeConverter.convert_type("Optional[Dict[(str, List[Any])]]")
    assert result == "Record<string, unknown[]> | null"


def test_convert_nested_list_preserves_dimension() -> None:
    result = TypeConverter.convert_type("List[List[float]]")
    assert result == "number[][]"

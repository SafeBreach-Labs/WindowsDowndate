import io
import xml.etree.ElementTree as ET
from typing import List, Union, Dict


class XmlElementAttributeNotFound(Exception):
    pass


def load_xml(path_or_buffer: Union[io.StringIO, io.BytesIO, str]) -> ET.ElementTree:
    return ET.parse(path_or_buffer)


def load_xml_from_buffer(xml_buffer: Union[str, bytes]) -> ET.ElementTree:
    if isinstance(xml_buffer, str):
        xml_buffer = io.StringIO(xml_buffer)
    elif isinstance(xml_buffer, bytes):
        xml_buffer = io.BytesIO(xml_buffer)
    else:
        raise Exception(f"Wrong type, expected str or bytes, received {type(xml_buffer)} instead")

    return load_xml(xml_buffer)


def find_child_elements_by_match(element: ET.ElementTree, match: str) -> List[ET.Element]:
    return element.findall(match)


def find_first_child_element_by_match(element: ET.ElementTree, match: str) -> ET.Element:
    return element.find(match)


def get_element_attribute(element: ET.Element, attribute: str) -> str:
    attribute_value = element.get(attribute)
    if not attribute_value:
        raise XmlElementAttributeNotFound(f"Failed to find attribute {attribute}")
    return attribute_value


def create_element(element_name: str, attributes: Dict[str, str]) -> ET.Element:
    element = ET.Element(element_name)

    for key, value in attributes.items():
        element.set(key, value)

    return element


def append_child_element(element: ET.Element, child_element: ET.Element) -> None:
    element.append(child_element)
    ET.indent(element, space="\t", level=1)

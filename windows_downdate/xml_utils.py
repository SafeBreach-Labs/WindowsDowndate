import io
import xml.etree.ElementTree as ET
from typing import List, Union, Dict


class XmlElementAttributeNotFound(Exception):
    """
    Exception to be raised when no XML element attribute is found
    """
    pass


def load_xml(path_or_buffer: Union[io.StringIO, io.BytesIO, str]) -> ET.ElementTree:
    """
    Loads XML from path or buffer

    :param path_or_buffer: Path to the XML file on disk or buffer of it
    :return: Initialized ET.ElementTree instance of the XML
    """
    return ET.parse(path_or_buffer)


def load_xml_from_buffer(xml_buffer: Union[str, bytes]) -> ET.ElementTree:
    """
    Loads XML from buffer

    :param xml_buffer: The XML buffer to load
    :return: Initialized ET.ElementTree instance of the XML
    :raises: Exception - if the xml_buffer type is not str or bytes
    """
    if isinstance(xml_buffer, str):
        xml_buffer = io.StringIO(xml_buffer)
    elif isinstance(xml_buffer, bytes):
        xml_buffer = io.BytesIO(xml_buffer)
    else:
        raise Exception(f"Wrong type, expected str or bytes, received {type(xml_buffer)} instead")

    return load_xml(xml_buffer)


def find_child_elements_by_match(element: ET.ElementTree, match: str) -> List[ET.Element]:
    """
    Finds all child elements by match

    :param element: The element to search for child elements in
    :param match: The match to search
    :return: List of initialized ET.Element elements
    """
    return element.findall(match)


def get_element_attribute(element: ET.Element, attribute: str) -> str:
    """
    Gets element attribute

    :param element: The element to get attribute gtom
    :param attribute: The attribute name
    :return: The attribute value
    :raises: XmlElementAttributeNotFound - if failed to find the requested attribute
    """
    attribute_value = element.get(attribute)
    if not attribute_value:
        raise XmlElementAttributeNotFound(f"Failed to find attribute {attribute}")
    return attribute_value


def create_element(element_name: str, attributes: Dict[str, str]) -> ET.Element:
    """
    Create an XML element

    :param element_name: The element name
    :param attributes: The element attributes
    :return: Initialized ET.Element instance of the created element
    """
    element = ET.Element(element_name)

    for key, value in attributes.items():
        element.set(key, value)

    return element


def append_child_element(element: ET.Element, child_element: ET.Element) -> None:
    """
    Appends child element to element

    :param element: The element to append child element to
    :param child_element: The child element
    :return: None
    """
    element.append(child_element)
    ET.indent(element, space="\t", level=1)

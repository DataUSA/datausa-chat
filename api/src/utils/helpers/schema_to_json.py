import xml.etree.ElementTree as ET
import json
import sys

def parse_xml_to_json(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    tables = []

    # Parse Shared Dimensions
    shared_dimensions = {}
    for shared_dimension in root.findall('.//SharedDimension'):
        shared_dimension_name = shared_dimension.get('name')
        hierarchy = shared_dimension.find('.//Hierarchy')
        hierarchy_name = hierarchy.get('name')
        levels = [level.get('name') for level in hierarchy.findall('.//Level')]
        shared_dimensions[shared_dimension_name] = {"hierarchy": hierarchy_name, "levels": levels}

    # Parse Cubes
    for cube in root.findall('.//Cube'):
        table_name = cube.get('name')

        measures = []
        dimensions = []
        table_description = None

        # Parse Measures
        for measure in cube.findall('.//Measure'):
            measure_name = measure.get('name')
            measure_description = measure.find('.//Annotation[@name="caption_en"]')
            measure_description = measure_description.text if measure_description is not None else ""
            measures.append({"name": measure_name, "description": measure_description})

        # Parse Cube-specific Dimensions
        for dimension in cube.findall('.//Dimension'):
            dimension_name = dimension.get('name')
            hierarchy_name = dimension.find('.//Hierarchy').get('name')
            levels = [level.get('name') for level in dimension.findall('.//Level')]
            dimensions.append({"name": dimension_name, "hierarchy": hierarchy_name, "levels": levels})

        # Parse Dimension Usage (Shared Dimensions)
        for dimension_usage in cube.findall('.//DimensionUsage'):
            dimension_name = dimension_usage.get('name')
            shared_dimension_name = dimension_usage.get('source')
            hierarchy_info = shared_dimensions.get(shared_dimension_name)
            hierarchy_name = hierarchy_info["hierarchy"]
            levels = hierarchy_info["levels"]
            dimensions.append({"name": dimension_name, "hierarchy": hierarchy_name, "levels": levels})

        # Parse Table Description
        table_annotation = cube.find('.//Annotation[@name="table_en"]')
        if table_annotation is not None:
            table_description = table_annotation.text

        tables.append({
            "name": table_name,
            "api": "Tesseract",
            "description": table_description,
            "measures": measures,
            "dimensions": [
                {
                    "name": dimension["name"],
                    "description": f"{dimension['name']} dimension of the data.",
                    "hierarchies": [
                        {
                            "name": dimension["hierarchy"],
                            "levels": dimension["levels"]
                        }
                    ]
                } for dimension in dimensions
            ]
        })

    return {"tables": tables}


def main(input_file, output_file):
    xml_file = input_file
    json_output = parse_xml_to_json(xml_file)
    print(json.dumps(json_output, indent=4))

    with open(output_file, 'w') as f:
        json.dump(json_output, f, indent=4)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python schema_to_json.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    main(input_file, output_file)
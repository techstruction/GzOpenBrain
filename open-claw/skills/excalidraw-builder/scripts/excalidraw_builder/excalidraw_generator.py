import json
import argparse
from Excalidraw_Interface import SketchBuilder

import os

def create_diagram(data, output_path):
    """
    Creates an excalidraw representation from a structured dict.
    """
    # Ensure the directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    sketch = SketchBuilder()
    
    node_map = {}
    
    # 1. First Pass: Create Nodes
    for n in data.get("nodes", []):
        shape_type = n.get("shape", "Rectangle").lower()
        x = n.get("x", 0)
        y = n.get("y", 0)
        label = n.get("label", "")
        # TextBox auto calculates width/height, we shouldn't force it in kwargs
        width = n.get("width", 150)
        height = n.get("height", 60)
        bg_color = n.get("backgroundColor", "transparent")
        
        node_obj = None
        if shape_type == "diamond":
            if label:
                node_obj = sketch.Diamond(x, y, width, height, backgroundColor=bg_color)
                # Text roughly centered
                sketch.Text(label, x, y)
            else:
                node_obj = sketch.Diamond(x, y, width, height, backgroundColor=bg_color)
                
        elif shape_type == "ellipse":
            if label:
                node_obj = sketch.Ellipse(x, y, width, height, backgroundColor=bg_color)
                sketch.Text(label, x, y)
            else:
                node_obj = sketch.Ellipse(x, y, width, height, backgroundColor=bg_color)
                
        elif shape_type == "text":
            node_obj = sketch.Text(label, x, y, backgroundColor=bg_color)
            
        else: # Default Rectangle
            if label:
                # Use TextBox which has automatic sizing around the text, only pass backgroundColor
                node_obj = sketch.TextBox(label, x, y, rect_kwargs={"backgroundColor": bg_color})
            else:
                node_obj = sketch.Rectangle(x, y, width, height, backgroundColor=bg_color)
                
        node_map[n["id"]] = node_obj
        
    # 2. Second Pass: Create Edges
    for e in data.get("edges", []):
        from_id = e.get("from")
        to_id = e.get("to")
        
        if from_id in node_map and to_id in node_map:
            from_node = node_map[from_id]
            to_node = node_map[to_id]
            
            # Draw bound arrows using the builder helper
            # Default arrow is Arrow, but could use DoubleArrow
            sketch.create_binding_arrows(from_node, to_node)
            
            label = e.get("label")
            if label:
                 # Approximate the middle to add text
                 try:
                     nx = sum([from_node.x, to_node.x]) / 2
                     ny = sum([from_node.y, to_node.y]) / 2
                     sketch.Text(label, nx, ny)
                 except Exception:
                     pass
                
    # Save the sketch
    sketch.export_to_file(output_path)
    print(f"✅ Successfully written to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Excalidraw file from JSON.")
    parser.add_argument("input_json", help="Path to input JSON describing the diagram")
    parser.add_argument("output_path", help="Path to save the resulting .excalidraw file")
    
    args = parser.parse_args()
    
    # Handle default folder 'Excalidrawings' if only a filename is provided
    output_path = args.output_path
    if not os.path.dirname(output_path):
        output_path = os.path.join("Excalidrawings", output_path)
    
    with open(args.input_json, "r") as f:
        data = json.load(f)
        
    create_diagram(data, output_path)

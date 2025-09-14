#!/usr/bin/env python3
"""
FastMCP server for Manim mathematical animation engine.

This server provides programmatic access to Manim's core functionality
including animation creation, mobject manipulation, text rendering,
3D graphics, and scene management.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List

from fastmcp import FastMCP

# Import Manim core functionality
import manim
from manim import *
from manim.animation.animation import Animation
from manim.mobject.mobject import Mobject
from manim.scene.scene import Scene

# Initialize FastMCP server
mcp = FastMCP("manim", dependencies=["manim"])


@mcp.tool()
async def create_animation(
    animation_type: str,
    mobject_data: Dict[str, Any],
    duration: float = 1.0,
    output_format: str = "mp4",
    resolution: str = "hd",
    **kwargs: Any
) -> Dict[str, Any]:
    """Create and execute a Manim animation.
    
    Args:
        animation_type: Type of animation (Create, Write, FadeIn, FadeOut, Transform, etc.)
        mobject_data: Data to create the mobject to animate
        duration: Animation duration in seconds
        output_format: Output format (mp4, gif, png)
        resolution: Output resolution (hd, full_hd, 4k)
        **kwargs: Additional animation parameters
        
    Returns:
        Dictionary with animation results and metadata
    """
    try:
        # Create mobject from data
        mobject = create_mobject_from_data(mobject_data)
        
        # Create animation based on type
        animation_class = getattr(manim, animation_type, None)
        if not animation_class or not issubclass(animation_class, Animation):
            return {"error": f"Invalid animation type: {animation_type}"}
        
        animation = animation_class(mobject, run_time=duration, **kwargs)
        
        # Configure output settings
        resolution_map = {
            "hd": (1280, 720),
            "full_hd": (1920, 1080), 
            "4k": (3840, 2160)
        }
        
        width, height = resolution_map.get(resolution, (1280, 720))
        
        # Create temporary scene and render
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = f"animation.{output_format}"
            output_path = Path(temp_dir) / output_file
            
            class TempScene(Scene):
                def construct(self):
                    self.play(animation)
            
            # Configure scene with proper settings
            scene = TempScene()
            scene.renderer.file_writer.output_directory = temp_dir
            
            # Set resolution
            scene.camera.pixel_width = width
            scene.camera.pixel_height = height
            scene.camera.frame_width = width / 100
            scene.camera.frame_height = height / 100
            
            scene.render()
            
            return {
                "success": True,
                "animation_type": animation_type,
                "duration": duration,
                "output_format": output_format,
                "resolution": resolution,
                "output_path": str(output_path),
                "file_size": output_path.stat().st_size if output_path.exists() else 0
            }
            
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


def create_mobject_from_data(data: Dict[str, Any]) -> Mobject:
    """Create a Mobject from serialized data."""
    mobject_type = data.get("type")
    params = data.get("params", {})
    
    # Basic geometry
    if mobject_type == "circle":
        return Circle(**params)
    elif mobject_type == "square":
        return Square(**params)
    elif mobject_type == "line":
        return Line(**params)
    elif mobject_type == "triangle":
        return Triangle(**params)
    elif mobject_type == "polygon":
        return Polygon(**params)
    elif mobject_type == "arc":
        return Arc(**params)
    
    # Text and math
    elif mobject_type == "text":
        return Text(**params)
    elif mobject_type == "tex":
        return MathTex(**params)
    elif mobject_type == "code":
        return Code(**params)
    
    # 3D objects
    elif mobject_type == "sphere":
        return Sphere(**params)
    elif mobject_type == "cube":
        return Cube(**params)
    elif mobject_type == "cylinder":
        return Cylinder(**params)
    elif mobject_type == "cone":
        return Cone(**params)
    elif mobject_type == "torus":
        return Torus(**params)
    
    # Graphing and coordinate systems
    elif mobject_type == "axes":
        return Axes(**params)
    elif mobject_type == "number_line":
        return NumberLine(**params)
    elif mobject_type == "coordinate_system":
        return CoordinateSystem(**params)
    elif mobject_type == "function_graph":
        func = params.get("function")
        x_range = params.get("x_range", [-5, 5, 0.1])
        return FunctionGraph(func, x_range, **{k: v for k, v in params.items() if k not in ["function", "x_range"]})
    
    # Tables and matrices
    elif mobject_type == "table":
        return Table(**params)
    elif mobject_type == "matrix":
        return Matrix(**params)
    
    # Specialized mobjects
    elif mobject_type == "vector":
        return Vector(**params)
    elif mobject_type == "vector_field":
        return VectorField(**params)
    elif mobject_type == "value_tracker":
        return ValueTracker(**params)
    elif mobject_type == "image_mobject":
        return ImageMobject(**params)
    
    # Groups
    elif mobject_type == "vgroup":
        mobjects = [create_mobject_from_data(mobj_data) for mobj_data in params.get("mobjects", [])]
        return VGroup(*mobjects)
    
    else:
        raise ValueError(f"Unknown mobject type: {mobject_type}")


@mcp.tool()
async def create_mobject(
    mobject_type: str,
    **kwargs: Any
) -> Dict[str, Any]:
    """Create a Manim mobject (mathematical object).
    
    Args:
        mobject_type: Type of mobject to create
        **kwargs: Parameters for the mobject creation
        
    Returns:
        Serialized representation of the created mobject
    """
    try:
        mobject_class = getattr(manim, mobject_type, None)
        if not mobject_class or not issubclass(mobject_class, Mobject):
            return {"error": f"Invalid mobject type: {mobject_type}"}
        
        mobject = mobject_class(**kwargs)
        
        return {
            "success": True,
            "mobject_type": mobject_type,
            "position": mobject.get_center().tolist(),
            "bounds": mobject.get_bounding_box().tolist(),
            "width": mobject.width,
            "height": mobject.height,
            "depth": mobject.depth if hasattr(mobject, 'depth') else 0
        }
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def create_vector_field(
    function: str,
    x_range: List[float] = [-5, 5, 1],
    y_range: List[float] = [-5, 5, 1],
    color_scheme: str = "heat",
    **kwargs: Any
) -> Dict[str, Any]:
    """Create a vector field from a vector function.
    
    Args:
        function: Vector function as string (e.g., "[x, y]" or "[y, -x]")
        x_range: X range for the field [min, max, step]
        y_range: Y range for the field [min, max, step]
        color_scheme: Color scheme for vectors (heat, rainbow, etc.)
        **kwargs: Additional vector field parameters
        
    Returns:
        Vector field information
    """
    try:
        # Safe evaluation of vector function
        import math
        import numpy as np
        
        allowed_names = {**math.__dict__, **np.__dict__}
        code = compile(function, "<string>", "eval")
        
        for name in code.co_names:
            if name not in allowed_names:
                return {"error": f"Function contains disallowed name: {name}"}
        
        vector_func = lambda x, y: eval(code, {"__builtins__": {}}, {**allowed_names, "x": x, "y": y})
        
        mobject = VectorField(
            vector_func,
            x_range=x_range[:2],
            y_range=y_range[:2],
            color_scheme=color_scheme,
            **kwargs
        )
        
        return {
            "success": True,
            "mobject_type": "VectorField",
            "function": function,
            "x_range": x_range,
            "y_range": y_range,
            "bounds": mobject.get_bounding_box().tolist(),
            "vector_count": len(mobject.vectors) if hasattr(mobject, 'vectors') else 0
        }
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def create_image_mobject(
    image_path: str = None,
    image_data: str = None,
    width: float = 4,
    height: float = 3,
    **kwargs: Any
) -> Dict[str, Any]:
    """Create an image mobject from file path or base64 data.
    
    Args:
        image_path: Path to image file (optional)
        image_data: Base64 encoded image data (optional)
        width: Desired width of the image
        height: Desired height of the image
        **kwargs: Additional image parameters
        
    Returns:
        Image mobject information
    """
    try:
        if image_path:
            mobject = ImageMobject(image_path, **kwargs)
        elif image_data:
            # Handle base64 image data
            import base64
            from io import BytesIO
            from PIL import Image
            
            # Decode base64 and create image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
            
            # Create temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                image.save(tmp.name)
                mobject = ImageMobject(tmp.name, **kwargs)
        else:
            return {"error": "Either image_path or image_data must be provided"}
        
        # Scale to desired dimensions
        mobject.set_width(width)
        mobject.set_height(height)
        
        return {
            "success": True,
            "mobject_type": "ImageMobject",
            "width": mobject.width,
            "height": mobject.height,
            "bounds": mobject.get_bounding_box().tolist(),
            "has_alpha": hasattr(mobject, 'has_alpha') and mobject.has_alpha
        }
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def transform_mobject(
    mobject_data: Dict[str, Any],
    transformation: str,
    **kwargs: Any
) -> Dict[str, Any]:
    """Apply a transformation to a mobject.
    
    Args:
        mobject_data: Serialized mobject data
        transformation: Transformation type (scale, rotate, shift, etc.)
        **kwargs: Transformation parameters
        
    Returns:
        Transformed mobject data
    """
    try:
        mobject = create_mobject_from_data(mobject_data)
        
        # Apply transformation
        if transformation == "scale":
            factor = kwargs.get("factor", 1.0)
            mobject.scale(factor)
        elif transformation == "rotate":
            angle = kwargs.get("angle", 0)
            axis = kwargs.get("axis", OUT)
            mobject.rotate(angle, axis)
        elif transformation == "shift":
            vector = kwargs.get("vector", [0, 0, 0])
            mobject.shift(np.array(vector))
        elif transformation == "move_to":
            point = kwargs.get("point", [0, 0, 0])
            mobject.move_to(np.array(point))
        elif transformation == "set_color":
            color = kwargs.get("color", "WHITE")
            mobject.set_color(color)
        else:
            return {"error": f"Unknown transformation: {transformation}"}
        
        return {
            "success": True,
            "transformation": transformation,
            "new_position": mobject.get_center().tolist(),
            "new_bounds": mobject.get_bounding_box().tolist()
        }
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def create_mobject_group(
    mobjects_data: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Create a group of mobjects (VGroup).
    
    Args:
        mobjects_data: List of serialized mobject data
        
    Returns:
        Group information and bounds
    """
    try:
        mobjects = [create_mobject_from_data(data) for data in mobjects_data]
        group = VGroup(*mobjects)
        
        return {
            "success": True,
            "group_type": "VGroup",
            "mobject_count": len(mobjects),
            "position": group.get_center().tolist(),
            "bounds": group.get_bounding_box().tolist(),
            "width": group.width,
            "height": group.height
        }
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def get_mobject_properties(
    mobject_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Get detailed properties of a mobject.
    
    Args:
        mobject_data: Serialized mobject data
        
    Returns:
        Detailed mobject properties
    """
    try:
        mobject = create_mobject_from_data(mobject_data)
        
        properties = {
            "position": mobject.get_center().tolist(),
            "bounds": mobject.get_bounding_box().tolist(),
            "width": mobject.width,
            "height": mobject.height,
            "depth": getattr(mobject, 'depth', 0),
            "color": str(mobject.color) if hasattr(mobject, 'color') else None,
            "stroke_width": getattr(mobject, 'stroke_width', None),
            "fill_opacity": getattr(mobject, 'fill_opacity', None)
        }
        
        return {"success": True, "properties": properties}
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def create_coordinate_system(
    system_type: str = "axes",
    x_range: List[float] = [-5, 5, 1],
    y_range: List[float] = [-5, 5, 1],
    **kwargs: Any
) -> Dict[str, Any]:
    """Create a coordinate system for graphing.
    
    Args:
        system_type: Type of coordinate system (axes, number_line, etc.)
        x_range: X-axis range [min, max, step]
        y_range: Y-axis range [min, max, step]
        **kwargs: Additional parameters
        
    Returns:
        Coordinate system information
    """
    try:
        if system_type == "axes":
            mobject = Axes(x_range=x_range[:2], y_range=y_range[:2], **kwargs)
        elif system_type == "number_line":
            mobject = NumberLine(x_range=x_range[:2], **kwargs)
        elif system_type == "complex_plane":
            mobject = ComplexPlane(**kwargs)
        else:
            return {"error": f"Unknown coordinate system type: {system_type}"}
        
        return {
            "success": True,
            "system_type": system_type,
            "bounds": mobject.get_bounding_box().tolist(),
            "width": mobject.width,
            "height": mobject.height
        }
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def plot_function(
    function: str,
    x_range: List[float] = [-5, 5, 0.1],
    color: str = "BLUE",
    **kwargs: Any
) -> Dict[str, Any]:
    """Plot a mathematical function.
    
    Args:
        function: Mathematical function as string (e.g., "x**2")
        x_range: X range for plotting [min, max, step]
        color: Function color
        **kwargs: Additional parameters
        
    Returns:
        Function graph information
    """
    try:
        # Create function from string
        import math
        import numpy as np
        
        # Safe evaluation of function string
        allowed_names = {**math.__dict__, **np.__dict__}
        code = compile(function, "<string>", "eval")
        
        for name in code.co_names:
            if name not in allowed_names:
                return {"error": f"Function contains disallowed name: {name}"}
        
        func = lambda x: eval(code, {"__builtins__": {}}, {**allowed_names, "x": x})
        
        mobject = FunctionGraph(func, x_range, color=color, **kwargs)
        
        return {
            "success": True,
            "function": function,
            "x_range": x_range,
            "bounds": mobject.get_bounding_box().tolist(),
            "length": mobject.length
        }
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def create_graph(
    vertices: List[List[float]],
    edges: List[List[int]],
    labels: bool = False,
    **kwargs: Any
) -> Dict[str, Any]:
    """Create a graph from vertices and edges.
    
    Args:
        vertices: List of vertex coordinates [[x1, y1], [x2, y2], ...]
        edges: List of edges [[i1, i2], [i3, i4], ...]
        labels: Whether to add vertex labels
        **kwargs: Additional parameters
        
    Returns:
        Graph information
    """
    try:
        mobject = Graph(vertices, edges, labels=labels, **kwargs)
        
        return {
            "success": True,
            "vertex_count": len(vertices),
            "edge_count": len(edges),
            "bounds": mobject.get_bounding_box().tolist()
        }
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool() 
async def render_text(
    text: str,
    is_latex: bool = False,
    font_size: int = 48,
    color: str = "WHITE",
    font: str = None,
    weight: str = None,
    slant: str = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """Render text using Manim's text rendering system.
    
    Args:
        text: Text content to render
        is_latex: Whether to render as LaTeX
        font_size: Font size in points
        color: Text color
        font: Font family name
        weight: Font weight (NORMAL, BOLD, etc.)
        slant: Font slant (NORMAL, ITALIC, etc.)
        **kwargs: Additional text parameters
        
    Returns:
        Information about the rendered text
    """
    try:
        text_kwargs = {
            "font_size": font_size,
            "color": color,
            **kwargs
        }
        
        if font:
            text_kwargs["font"] = font
        if weight:
            text_kwargs["weight"] = weight
        if slant:
            text_kwargs["slant"] = slant
        
        if is_latex:
            mobject = MathTex(text, **text_kwargs)
        else:
            mobject = Text(text, **text_kwargs)
        
        return {
            "success": True,
            "text": text,
            "is_latex": is_latex,
            "bounds": mobject.get_bounding_box().tolist(),
            "width": mobject.width,
            "height": mobject.height,
            "font_size": font_size,
            "color": color
        }
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def render_latex_equation(
    equation: str,
    font_size: int = 48,
    color: str = "WHITE",
    **kwargs: Any
) -> Dict[str, Any]:
    """Render a LaTeX mathematical equation.
    
    Args:
        equation: LaTeX equation string
        font_size: Font size in points
        color: Text color
        **kwargs: Additional LaTeX parameters
        
    Returns:
        Information about the rendered equation
    """
    try:
        mobject = MathTex(equation, font_size=font_size, color=color, **kwargs)
        
        return {
            "success": True,
            "equation": equation,
            "bounds": mobject.get_bounding_box().tolist(),
            "width": mobject.width,
            "height": mobject.height,
            "font_size": font_size
        }
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def create_text_animation(
    text: str,
    animation_type: str = "Write",
    is_latex: bool = False,
    font_size: int = 48,
    color: str = "WHITE",
    duration: float = 1.0,
    **kwargs: Any
) -> Dict[str, Any]:
    """Create an animation for text rendering.
    
    Args:
        text: Text content to animate
        animation_type: Type of animation (Write, AddTextLetterByLetter, etc.)
        is_latex: Whether to render as LaTeX
        font_size: Font size in points
        color: Text color
        duration: Animation duration
        **kwargs: Additional parameters
        
    Returns:
        Animation results
    """
    try:
        # Create text mobject
        if is_latex:
            mobject = MathTex(text, font_size=font_size, color=color, **kwargs)
        else:
            mobject = Text(text, font_size=font_size, color=color, **kwargs)
        
        # Create animation
        animation_class = getattr(manim, animation_type, None)
        if not animation_class or not issubclass(animation_class, Animation):
            return {"error": f"Invalid animation type for text: {animation_type}"}
        
        animation = animation_class(mobject, run_time=duration)
        
        # Render animation
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "text_animation.mp4"
            
            class TempScene(Scene):
                def construct(self):
                    self.play(animation)
            
            scene = TempScene()
            scene.renderer.file_writer.output_directory = temp_dir
            scene.render()
            
            return {
                "success": True,
                "animation_type": animation_type,
                "text": text,
                "is_latex": is_latex,
                "duration": duration,
                "output_path": str(output_path)
            }
            
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def create_table(
    data: List[List[Any]],
    row_labels: List[str] = None,
    col_labels: List[str] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """Create a table from data.
    
    Args:
        data: 2D list of table data
        row_labels: List of row labels
        col_labels: List of column labels
        **kwargs: Additional table parameters
        
    Returns:
        Table information
    """
    try:
        mobject = Table(
            data,
            row_labels=row_labels,
            col_labels=col_labels,
            **kwargs
        )
        
        return {
            "success": True,
            "rows": len(data),
            "columns": len(data[0]) if data else 0,
            "bounds": mobject.get_bounding_box().tolist(),
            "width": mobject.width,
            "height": mobject.height
        }
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def create_matrix(
    matrix_data: List[List[Any]],
    bracket_type: str = "square",
    **kwargs: Any
) -> Dict[str, Any]:
    """Create a matrix from data.
    
    Args:
        matrix_data: 2D list of matrix elements
        bracket_type: Type of brackets ("square", "round", "curly")
        **kwargs: Additional matrix parameters
        
    Returns:
        Matrix information
    """
    try:
        mobject = Matrix(matrix_data, bracket_type=bracket_type, **kwargs)
        
        return {
            "success": True,
            "rows": len(matrix_data),
            "columns": len(matrix_data[0]) if matrix_data else 0,
            "bounds": mobject.get_bounding_box().tolist(),
            "width": mobject.width,
            "height": mobject.height
        }
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def get_available_fonts() -> List[str]:
    """Get list of available fonts for text rendering."""
    try:
        # This would need proper font discovery
        # For now, return common fonts
        common_fonts = [
            "Arial", "Times New Roman", "Courier New", "Helvetica", 
            "Verdana", "Georgia", "Palatino", "Garamond"
        ]
        return common_fonts
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def create_3d_mobject(
    mobject_type: str,
    **kwargs: Any
) -> Dict[str, Any]:
    """Create a 3D mobject.
    
    Args:
        mobject_type: Type of 3D mobject (Sphere, Cube, Cylinder, etc.)
        **kwargs: Parameters for 3D mobject creation
        
    Returns:
        Information about the created 3D mobject
    """
    try:
        # Check if 3D capabilities are available
        if not hasattr(manim, "ThreeDScene"):
            return {"error": "3D functionality not available"}
        
        mobject_class = getattr(manim, mobject_type, None)
        if not mobject_class:
            return {"error": f"3D mobject type not found: {mobject_type}"}
        
        mobject = mobject_class(**kwargs)
        
        return {
            "success": True,
            "mobject_type": mobject_type,
            "position": mobject.get_center().tolist(),
            "bounds": mobject.get_bounding_box().tolist(),
            "width": mobject.width,
            "height": mobject.height,
            "depth": getattr(mobject, 'depth', 0)
        }
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def create_3d_animation(
    mobject_data: Dict[str, Any],
    animation_type: str,
    duration: float = 1.0,
    camera_position: List[float] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """Create a 3D animation.
    
    Args:
        mobject_data: Serialized 3D mobject data
        animation_type: Type of 3D animation
        duration: Animation duration
        camera_position: Custom camera position [x, y, z]
        **kwargs: Additional animation parameters
        
    Returns:
        3D animation results
    """
    try:
        if not hasattr(manim, "ThreeDScene"):
            return {"error": "3D functionality not available"}
        
        mobject = create_mobject_from_data(mobject_data)
        
        animation_class = getattr(manim, animation_type, None)
        if not animation_class or not issubclass(animation_class, Animation):
            return {"error": f"Invalid 3D animation type: {animation_type}"}
        
        animation = animation_class(mobject, run_time=duration, **kwargs)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "3d_animation.mp4"
            
            class Temp3DScene(ThreeDScene):
                def construct(self):
                    if camera_position:
                        self.set_camera_orientation(
                            phi=75 * DEGREES,
                            theta=30 * DEGREES,
                            distance=6,
                            frame_center=np.array(camera_position)
                        )
                    self.play(animation)
            
            scene = Temp3DScene()
            scene.renderer.file_writer.output_directory = temp_dir
            scene.render()
            
            return {
                "success": True,
                "animation_type": animation_type,
                "duration": duration,
                "output_path": str(output_path)
            }
            
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def check_3d_capabilities() -> Dict[str, Any]:
    """Check if 3D and OpenGL capabilities are available."""
    capabilities = {
        "3d_available": hasattr(manim, "ThreeDScene"),
        "opengl_available": hasattr(manim, "opengl"),
        "shader_support": hasattr(manim, "Shader") if hasattr(manim, "opengl") else False,
        "3d_mobjects_available": hasattr(manim, "Sphere") and hasattr(manim, "Cube")
    }
    
    return {"success": True, "capabilities": capabilities}


@mcp.tool()
async def list_3d_mobjects() -> List[str]:
    """List available 3D mobject types."""
    try:
        if not hasattr(manim, "ThreeDScene"):
            return []
        
        # Common 3D mobjects
        mobjects_3d = [
            "Sphere", "Cube", "Cylinder", "Cone", "Torus", 
            "Arrow3D", "Line3D", "Dot3D"
        ]
        
        available_mobjects = []
        for mobject in mobjects_3d:
            if hasattr(manim, mobject):
                available_mobjects.append(mobject)
        
        return available_mobjects
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def create_scene(
    scene_definition: Dict[str, Any],
    output_format: str = "mp4",
    resolution: str = "hd",
    output_directory: str = None
) -> Dict[str, Any]:
    """Create and render a complete Manim scene.
    
    Args:
        scene_definition: Scene definition with construct method logic
        output_format: Output format (mp4, gif, png)
        resolution: Output resolution (hd, full_hd, 4k)
        output_directory: Custom output directory (optional)
        
    Returns:
        Scene rendering results
    """
    try:
        resolution_map = {
            "hd": (1280, 720),
            "full_hd": (1920, 1080), 
            "4k": (3840, 2160)
        }
        
        width, height = resolution_map.get(resolution, (1280, 720))
        
        # Create dynamic scene class
        scene_code = scene_definition.get("construct_code", "")
        scene_name = scene_definition.get("name", "CustomScene")
        
        # Create the scene class dynamically
        exec_globals = {"manim": manim, "np": np}
        exec_locals = {}
        
        class_def = f"""
class {scene_name}(Scene):
    def construct(self):
        {scene_code}
"""
        
        exec(class_def, exec_globals, exec_locals)
        scene_class = exec_locals[scene_name]
        
        # Determine output directory
        if output_directory:
            output_dir = Path(output_directory)
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = Path(tempfile.mkdtemp())
        
        output_path = output_dir / f"{scene_name}.{output_format}"
        
        # Render the scene
        scene = scene_class()
        scene.renderer.file_writer.output_directory = str(output_dir)
        
        scene.camera.pixel_width = width
        scene.camera.pixel_height = height
        scene.camera.frame_width = width / 100
        scene.camera.frame_height = height / 100
        
        scene.render()
        
        return {
            "success": True,
            "scene_name": scene_name,
            "output_format": output_format,
            "output_path": str(output_path),
            "file_size": output_path.stat().st_size if output_path.exists() else 0
        }
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def create_specialized_scene(
    scene_type: str,
    scene_definition: Dict[str, Any],
    output_format: str = "mp4",
    resolution: str = "hd",
    output_directory: str = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """Create and render a specialized Manim scene.
    
    Args:
        scene_type: Type of specialized scene (MovingCameraScene, ZoomedScene, 
                   ThreeDScene, VectorScene, LinearTransformationScene)
        scene_definition: Scene definition with construct method logic
        output_format: Output format (mp4, gif, png)
        resolution: Output resolution (hd, full_hd, 4k)
        output_directory: Custom output directory (optional)
        **kwargs: Additional scene-specific parameters
        
    Returns:
        Scene rendering results
    """
    try:
        resolution_map = {
            "hd": (1280, 720),
            "full_hd": (1920, 1080), 
            "4k": (3840, 2160)
        }
        
        width, height = resolution_map.get(resolution, (1280, 720))
        
        # Create dynamic scene class with proper inheritance
        scene_code = scene_definition.get("construct_code", "")
        scene_name = scene_definition.get("name", f"Custom{scene_type}")
        
        # Import the specialized scene class
        scene_class_obj = getattr(manim, scene_type, None)
        if not scene_class_obj or not issubclass(scene_class_obj, Scene):
            return {"error": f"Invalid specialized scene type: {scene_type}"}
        
        # Create the scene class dynamically
        exec_globals = {"manim": manim, "np": np, scene_type: scene_class_obj}
        exec_locals = {}
        
        class_def = f"""
class {scene_name}({scene_type}):
    def construct(self):
        {scene_code}
"""
        
        exec(class_def, exec_globals, exec_locals)
        scene_class = exec_locals[scene_name]
        
        # Determine output directory
        if output_directory:
            output_dir = Path(output_directory)
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = Path(tempfile.mkdtemp())
        
        output_path = output_dir / f"{scene_name}.{output_format}"
        
        # Render the scene
        scene = scene_class()
        scene.renderer.file_writer.output_directory = str(output_dir)
        
        scene.camera.pixel_width = width
        scene.camera.pixel_height = height
        scene.camera.frame_width = width / 100
        scene.camera.frame_height = height / 100
        
        # Apply scene-specific parameters
        if scene_type == "ThreeDScene" and "camera_position" in kwargs:
            camera_pos = kwargs["camera_position"]
            scene.set_camera_orientation(
                phi=camera_pos.get("phi", 75 * DEGREES),
                theta=camera_pos.get("theta", 30 * DEGREES),
                distance=camera_pos.get("distance", 6),
                frame_center=np.array(camera_pos.get("frame_center", [0, 0, 0]))
            )
        
        scene.render()
        
        return {
            "success": True,
            "scene_type": scene_type,
            "scene_name": scene_name,
            "output_format": output_format,
            "output_path": str(output_path),
            "file_size": output_path.stat().st_size if output_path.exists() else 0
        }
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def list_specialized_scenes() -> List[str]:
    """List available specialized scene types in Manim."""
    specialized_scenes = [
        "MovingCameraScene", "ZoomedScene", "ThreeDScene", 
        "VectorScene", "LinearTransformationScene"
    ]
    
    available_scenes = []
    for scene_type in specialized_scenes:
        if hasattr(manim, scene_type):
            scene_class = getattr(manim, scene_type)
            if isinstance(scene_class, type) and issubclass(scene_class, Scene):
                available_scenes.append(scene_type)
    
    return available_scenes


@mcp.tool()
async def get_scene_config() -> Dict[str, Any]:
    """Get current Manim scene configuration."""
    try:
        from manim import config
        
        config_info = {
            "pixel_width": config.pixel_width,
            "pixel_height": config.pixel_height,
            "frame_width": config.frame_width,
            "frame_height": config.frame_height,
            "fps": config.fps,
            "renderer": config.renderer,
            "media_dir": config.media_dir,
            "video_dir": config.video_dir,
            "images_dir": config.images_dir,
            "tex_dir": config.tex_dir,
            "text_dir": config.text_dir,
            "partial_movie_dir": config.partial_movie_dir
        }
        
        return {"success": True, "config": config_info}
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def set_scene_config(
    **kwargs: Any
) -> Dict[str, Any]:
    """Set Manim scene configuration parameters."""
    try:
        from manim import tempconfig
        
        # Use tempconfig for temporary configuration changes
        with tempconfig(kwargs):
            return {
                "success": True,
                "message": "Configuration updated temporarily",
                "new_config": kwargs
            }
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def list_scene_types() -> List[str]:
    """List available scene types in Manim."""
    scene_classes = []
    for name in dir(manim):
        obj = getattr(manim, name)
        if isinstance(obj, type) and issubclass(obj, Scene) and obj != Scene:
            scene_classes.append(name)
    return sorted(scene_classes)


@mcp.tool()
async def render_example_scene(
    scene_type: str = "SquareToCircle",
    output_format: str = "mp4",
    resolution: str = "hd"
) -> Dict[str, Any]:
    """Render a built-in example scene.
    
    Args:
        scene_type: Type of example scene
        output_format: Output format
        resolution: Output resolution
        
    Returns:
        Rendering results
    """
    try:
        # Simple example scene if specific one not found
        if scene_type == "SquareToCircle":
            class SquareToCircle(Scene):
                def construct(self):
                    circle = Circle()
                    square = Square()
                    square.flip(RIGHT)
                    square.rotate(-3 * TAU / 8)
                    circle.set_fill(PINK, opacity=0.5)
                    
                    self.play(Create(square))
                    self.play(Transform(square, circle))
                    self.play(FadeOut(square))
            
            scene_class = SquareToCircle
        else:
            scene_class = getattr(manim, scene_type, None)
            if not scene_class or not issubclass(scene_class, Scene):
                return {"error": f"Scene type not found: {scene_type}"}
        
        resolution_map = {
            "hd": (1280, 720),
            "full_hd": (1920, 1080), 
            "4k": (3840, 2160)
        }
        
        width, height = resolution_map.get(resolution, (1280, 720))
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / f"{scene_type}.{output_format}"
            
            scene = scene_class()
            scene.renderer.file_writer.output_directory = temp_dir
            
            scene.camera.pixel_width = width
            scene.camera.pixel_height = height
            scene.camera.frame_width = width / 100
            scene.camera.frame_height = height / 100
            
            scene.render()
            
            return {
                "success": True,
                "scene_type": scene_type,
                "output_format": output_format,
                "output_path": str(output_path),
                "file_size": output_path.stat().st_size if output_path.exists() else 0
            }
            
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def list_available_animations() -> List[str]:
    """List all available animation types in Manim."""
    animation_classes = []
    for name in dir(manim):
        obj = getattr(manim, name)
        if isinstance(obj, type) and issubclass(obj, Animation) and obj != Animation:
            animation_classes.append(name)
    return sorted(animation_classes)


@mcp.tool()
async def create_animation_sequence(
    animations: List[Dict[str, Any]],
    output_format: str = "mp4",
    resolution: str = "hd"
) -> Dict[str, Any]:
    """Create a sequence of multiple animations.
    
    Args:
        animations: List of animation definitions
        output_format: Output format (mp4, gif, png)
        resolution: Output resolution (hd, full_hd, 4k)
        
    Returns:
        Dictionary with animation sequence results
    """
    try:
        resolution_map = {
            "hd": (1280, 720),
            "full_hd": (1920, 1080), 
            "4k": (3840, 2160)
        }
        
        width, height = resolution_map.get(resolution, (1280, 720))
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = f"animation_sequence.{output_format}"
            output_path = Path(temp_dir) / output_file
            
            class TempScene(Scene):
                def construct(self):
                    for anim_def in animations:
                        anim_type = anim_def.get("type")
                        mobject_data = anim_def.get("mobject", {})
                        duration = anim_def.get("duration", 1.0)
                        
                        mobject = create_mobject_from_data(mobject_data)
                        animation_class = getattr(manim, anim_type, None)
                        
                        if animation_class and issubclass(animation_class, Animation):
                            animation = animation_class(mobject, run_time=duration)
                            self.play(animation)
            
            scene = TempScene()
            scene.renderer.file_writer.output_directory = temp_dir
            
            scene.camera.pixel_width = width
            scene.camera.pixel_height = height
            scene.camera.frame_width = width / 100
            scene.camera.frame_height = height / 100
            
            scene.render()
            
            return {
                "success": True,
                "animation_count": len(animations),
                "output_format": output_format,
                "output_path": str(output_path),
                "file_size": output_path.stat().st_size if output_path.exists() else 0
            }
            
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def create_advanced_animation_sequence(
    animations: List[Dict[str, Any]],
    output_format: str = "mp4",
    resolution: str = "hd",
    timing_mode: str = "sequential",
    **kwargs: Any
) -> Dict[str, Any]:
    """Create an advanced animation sequence with timing controls.
    
    Args:
        animations: List of animation definitions with advanced options
        output_format: Output format (mp4, gif, png)
        resolution: Output resolution (hd, full_hd, 4k)
        timing_mode: Timing mode (sequential, parallel, staggered, lag_ratio)
        **kwargs: Additional timing parameters
        
    Returns:
        Advanced animation sequence results
    """
    try:
        resolution_map = {
            "hd": (1280, 720),
            "full_hd": (1920, 1080), 
            "4k": (3840, 2160)
        }
        
        width, height = resolution_map.get(resolution, (1280, 720))
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = f"advanced_animation_sequence.{output_format}"
            output_path = Path(temp_dir) / output_file
            
            class TempScene(Scene):
                def construct(self):
                    animation_objects = []
                    
                    for anim_def in animations:
                        anim_type = anim_def.get("type")
                        mobject_data = anim_def.get("mobject", {})
                        duration = anim_def.get("duration", 1.0)
                        wait_time = anim_def.get("wait", 0.0)
                        
                        mobject = create_mobject_from_data(mobject_data)
                        animation_class = getattr(manim, anim_type, None)
                        
                        if animation_class and issubclass(animation_class, Animation):
                            animation = animation_class(mobject, run_time=duration)
                            animation_objects.append({
                                "animation": animation,
                                "wait": wait_time
                            })
                    
                    # Apply timing mode
                    if timing_mode == "sequential":
                        for anim_obj in animation_objects:
                            if anim_obj["wait"] > 0:
                                self.wait(anim_obj["wait"])
                            self.play(anim_obj["animation"])
                    
                    elif timing_mode == "parallel":
                        # Play all animations simultaneously
                        parallel_anims = [anim_obj["animation"] for anim_obj in animation_objects]
                        self.play(*parallel_anims)
                    
                    elif timing_mode == "staggered":
                        # Stagger animations with delays
                        lag_ratio = kwargs.get("lag_ratio", 0.5)
                        animations_list = [anim_obj["animation"] for anim_obj in animation_objects]
                        self.play(*animations_list, lag_ratio=lag_ratio)
                    
                    elif timing_mode == "lag_ratio":
                        # Custom lag ratio
                        lag_ratio = kwargs.get("lag_ratio", 0.5)
                        animations_list = [anim_obj["animation"] for anim_obj in animation_objects]
                        self.play(*animations_list, lag_ratio=lag_ratio)
            
            scene = TempScene()
            scene.renderer.file_writer.output_directory = temp_dir
            
            scene.camera.pixel_width = width
            scene.camera.pixel_height = height
            scene.camera.frame_width = width / 100
            scene.camera.frame_height = height / 100
            
            scene.render()
            
            return {
                "success": True,
                "animation_count": len(animations),
                "timing_mode": timing_mode,
                "output_format": output_format,
                "output_path": str(output_path),
                "file_size": output_path.stat().st_size if output_path.exists() else 0
            }
            
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def create_animation_group(
    animations: List[Dict[str, Any]],
    group_type: str = "parallel"
) -> Dict[str, Any]:
    """Create a group of animations to be played together.
    
    Args:
        animations: List of animation definitions
        group_type: Type of animation group (parallel, sequential, successions)
        **kwargs: Group parameters (lag_ratio, run_time, etc.)
        
    Returns:
        Animation group information
    """
    try:
        animation_objects = []
        
        for anim_def in animations:
            anim_type = anim_def.get("type")
            mobject_data = anim_def.get("mobject", {})
            duration = anim_def.get("duration", 1.0)
            
            mobject = create_mobject_from_data(mobject_data)
            animation_class = getattr(manim, anim_type, None)
            
            if animation_class and issubclass(animation_class, Animation):
                animation = animation_class(mobject, run_time=duration)
                animation_objects.append(animation)
        
        group_info = {
            "success": True,
            "group_type": group_type,
            "animation_count": len(animation_objects),
            "total_duration": sum(anim.run_time for anim in animation_objects),
            "animations": [{
                "type": type(anim).__name__,
                "duration": anim.run_time,
                "mobject_type": type(anim.mobject).__name__
            } for anim in animation_objects]
        }
        
        # Add group-specific parameters
        if group_type == "parallel" and animation_objects:
            group_info["max_duration"] = max(anim.run_time for anim in animation_objects)
        
        return group_info
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def create_animation_timeline(
    timeline: List[Dict[str, Any]],
    total_duration: float = 10.0
) -> Dict[str, Any]:
    """Create a complex animation timeline with precise timing.
    
    Args:
        timeline: List of timeline events with start_time and duration
        total_duration: Total timeline duration
        **kwargs: Additional timeline parameters
        
    Returns:
        Timeline information and preview
    """
    try:
        # Sort timeline by start time
        sorted_timeline = sorted(timeline, key=lambda x: x.get("start_time", 0))
        
        timeline_info = {
            "success": True,
            "total_duration": total_duration,
            "event_count": len(sorted_timeline),
            "events": [],
            "overlaps": []
        }
        
        # Analyze timeline
        for i, event in enumerate(sorted_timeline):
            start_time = event.get("start_time", 0)
            duration = event.get("duration", 1.0)
            end_time = start_time + duration
            anim_type = event.get("type", "Create")
            
            timeline_info["events"].append({
                "index": i,
                "type": anim_type,
                "start_time": start_time,
                "duration": duration,
                "end_time": end_time
            })
            
            # Check for overlaps
            if i > 0:
                prev_event = sorted_timeline[i - 1]
                prev_end = prev_event.get("start_time", 0) + prev_event.get("duration", 1.0)
                if start_time < prev_end:
                    timeline_info["overlaps"].append({
                        "event1": i - 1,
                        "event2": i,
                        "overlap_duration": prev_end - start_time
                    })
        
        return timeline_info
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def get_animation_info(animation_type: str) -> Dict[str, Any]:
    """Get detailed information about a specific animation type."""
    try:
        animation_class = getattr(manim, animation_type, None)
        if not animation_class or not issubclass(animation_class, Animation):
            return {"error": f"Animation type not found: {animation_type}"}
        
        # Get method signature and docstring
        import inspect
        
        sig = inspect.signature(animation_class.__init__)
        params = {}
        for name, param in sig.parameters.items():
            if name != 'self':
                params[name] = {
                    "type": str(param.annotation) if param.annotation != param.empty else "Any",
                    "default": param.default if param.default != param.empty else None,
                    "required": param.default == param.empty
                }
        
        return {
            "name": animation_type,
            "module": animation_class.__module__,
            "docstring": animation_class.__doc__,
            "parameters": params
        }
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def list_available_mobjects() -> List[str]:
    """List all available mobject types in Manim."""
    mobject_classes = []
    for name in dir(manim):
        obj = getattr(manim, name)
        if isinstance(obj, type) and issubclass(obj, Mobject) and obj != Mobject:
            mobject_classes.append(name)
    return sorted(mobject_classes)


@mcp.tool()
async def get_manim_info() -> Dict[str, Any]:
    """Get information about the Manim installation and capabilities."""
    return {
        "version": manim.__version__,
        "available_animations": await list_available_animations(),
        "available_mobjects": await list_available_mobjects(),
        "has_opengl": hasattr(manim, "opengl"),
        "has_3d": hasattr(manim, "ThreeDScene")
    }


@mcp.tool()
async def execute_cli_command(
    command: str,
    args: List[str] = None
) -> Dict[str, Any]:
    """Execute a Manim CLI command programmatically.
    
    Args:
        command: CLI command to execute
        args: Additional arguments for the command
        
    Returns:
        Command execution results
    """
    try:
        if args is None:
            args = []
            
        # This would need proper subprocess integration
        # For now, return mock response
        return {
            "success": True,
            "command": command,
            "args": args,
            "output": "CLI command execution simulated"
        }
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def execute_manim_command(
    command: str,
    args: List[str] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """Execute a Manim CLI command programmatically.
    
    Args:
        command: CLI command to execute (render, init, cfg, plugins, etc.)
        args: Additional command arguments
        **kwargs: Command options as keyword arguments
        
    Returns:
        Command execution results
    """
    try:
        if args is None:
            args = []
        
        # Convert kwargs to command line arguments
        cli_args = []
        for key, value in kwargs.items():
            if len(key) == 1:
                cli_args.append(f"-{key}")
            else:
                cli_args.append(f"--{key.replace('_', '-')}")
            if value is not True:  # Handle flags (boolean True)
                cli_args.append(str(value))
        
        # Build full command
        full_command = ["manim", command] + args + cli_args
        
        # Execute command using subprocess with proper working directory
        import subprocess
        import os
        
        # Use current working directory or the directory of the script being executed
        working_dir = os.getcwd()
        
        # For render commands, use the directory of the file being rendered
        if command == "render" and args:
            file_path = args[0]
            if os.path.exists(file_path):
                working_dir = os.path.dirname(os.path.abspath(file_path))
        
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            cwd=working_dir,
            timeout=300  # 5 minute timeout
        )
        
        # Parse common Manim output patterns
        output_info = {
            "success": result.returncode == 0,
            "command": " ".join(full_command),
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "execution_time": getattr(result, 'elapsed', 0)
        }
        
        # Extract additional info from stdout for common commands
        if command == "render" and result.returncode == 0:
            # Try to extract output file path from render output
            lines = result.stdout.split('\n')
            for line in lines:
                if "File ready at" in line:
                    output_info["output_file"] = line.split("File ready at")[1].strip()
                elif "Animation duration" in line:
                    output_info["animation_duration"] = line.split("Animation duration")[1].strip()
        
        return output_info
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def render_scene_file(
    file_path: str,
    scene_name: str = None,
    output_format: str = "mp4",
    resolution: str = "hd",
    **kwargs: Any
) -> Dict[str, Any]:
    """Render a scene from a Python file using CLI interface.
    
    Args:
        file_path: Path to the Python file containing scenes
        scene_name: Specific scene class name to render (optional)
        output_format: Output format
        resolution: Output resolution
        **kwargs: Additional render options
        
    Returns:
        Rendering results
    """
    try:
        # Build command arguments
        args = [file_path]
        if scene_name:
            args.append(scene_name)
        
        # Add format and resolution options
        kwargs["format"] = output_format
        
        # Handle resolution properly as separate width/height parameters
        resolution_map = {
            "hd": (1280, 720),
            "full_hd": (1920, 1080), 
            "4k": (3840, 2160)
        }
        
        if resolution in resolution_map:
            width, height = resolution_map[resolution]
            kwargs["resolution"] = f"{width},{height}"
        
        # Add quality preset if not specified
        if "quality" not in kwargs:
            kwargs["quality"] = "high_quality"
        
        return await execute_manim_command("render", args, **kwargs)
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def check_manim_health() -> Dict[str, Any]:
    """Check Manim installation health and dependencies."""
    try:
        result = await execute_manim_command("checkhealth")
        
        # Parse health check results
        health_info = {
            "manim_version": manim.__version__,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "health_check_passed": result.get("success", False),
            "health_output": result.get("stdout", "")
        }
        
        return {"success": True, "health_info": health_info}
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def list_available_commands() -> Dict[str, Any]:
    """List all available Manim CLI commands."""
    try:
        result = await execute_manim_command("--help")
        
        # Parse help output to extract commands
        commands = []
        lines = result.get("stdout", "").split('\n')
        in_commands_section = False
        
        for line in lines:
            if "Commands:" in line:
                in_commands_section = True
                continue
            if in_commands_section and line.strip() and not line.startswith(' '):
                command = line.split()[0]
                if command != "Commands:":
                    commands.append(command)
            elif in_commands_section and not line.strip():
                break
        
        return {
            "success": True,
            "commands": commands,
            "help_output": result.get("stdout", "")
        }
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def create_manim_project(
    project_name: str,
    template: str = "default"
) -> Dict[str, Any]:
    """Create a new Manim project with the specified template.
    
    Args:
        project_name: Name of the project to create
        template: Project template (default, minimal, full)
        
    Returns:
        Project creation results
    """
    try:
        result = await execute_manim_command("init", [project_name, "--template", template])
        
        return {
            "success": result.get("success", False),
            "project_name": project_name,
            "output": result.get("stdout", ""),
            "project_path": os.path.join(os.getcwd(), project_name)
        }
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def get_manim_config() -> Dict[str, Any]:
    """Get the current Manim configuration."""
    try:
        result = await execute_manim_command("cfg", ["show"])
        
        # Parse config output
        config_lines = result.get("stdout", "").split('\n')
        config_data = {}
        current_section = None
        
        for line in config_lines:
            line = line.strip()
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1]
                config_data[current_section] = {}
            elif '=' in line and current_section:
                key, value = line.split('=', 1)
                config_data[current_section][key.strip()] = value.strip()
        
        return {
            "success": result.get("success", False),
            "config": config_data,
            "raw_output": result.get("stdout", "")
        }
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def set_manim_config(
    section: str,
    key: str,
    value: str
) -> Dict[str, Any]:
    """Set a Manim configuration value.
    
    Args:
        section: Configuration section
        key: Configuration key
        value: New value
        
    Returns:
        Configuration update results
    """
    try:
        result = await execute_manim_command("cfg", ["set", section, key, value])
        
        return {
            "success": result.get("success", False),
            "section": section,
            "key": key,
            "value": value,
            "output": result.get("stdout", "")
        }
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def list_manim_plugins() -> Dict[str, Any]:
    """List available Manim plugins."""
    try:
        result = await execute_manim_command("plugins", ["list"])
        
        # Parse plugins output
        plugins = []
        lines = result.get("stdout", "").split('\n')
        
        for line in lines:
            if line.strip() and not line.startswith(' '):
                plugins.append(line.strip())
        
        return {
            "success": result.get("success", False),
            "plugins": plugins,
            "output": result.get("stdout", "")
        }
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


if __name__ == "__main__":
    mcp.run()
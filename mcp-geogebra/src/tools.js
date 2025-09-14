export const geogebraTools = [
  {
    name: "eval_command",
    description: "Execute a GeoGebra command and return the result",
    inputSchema: {
      type: "object",
      properties: {
        command: {
          type: "string",
          description: "GeoGebra command to execute (e.g., 'f(x)=x^2', 'Integral(f,0,1)')"
        }
      },
      required: ["command"]
    }
  },
  {
    name: "eval_command_cas",
    description: "Execute a CAS (Computer Algebra System) command in GeoGebra",
    inputSchema: {
      type: "object",
      properties: {
        command: {
          type: "string",
          description: "CAS command to execute (e.g., 'Solve(x^2=4,x)', 'Factor(x^2-4)')"
        },
        rounding: {
          type: "string",
          description: "Rounding precision (default: '2')",
          default: "2"
        }
      },
      required: ["command"]
    }
  },
  {
    name: "export_png",
    description: "Export the current GeoGebra construction as PNG image",
    inputSchema: {
      type: "object",
      properties: {
        exportScale: {
          type: "number",
          description: "Export scale factor (default: 1.0)",
          default: 1.0
        },
        transparent: {
          type: "boolean",
          description: "Whether to use transparent background (default: false)",
          default: false
        },
        dpi: {
          type: "number",
          description: "DPI resolution (default: 300)",
          default: 300
        },
        greyscale: {
          type: "boolean",
          description: "Whether to export as greyscale (default: false)",
          default: false
        }
      }
    }
  },
  {
    name: "export_pdf",
    description: "Export the current GeoGebra construction as PDF document",
    inputSchema: {
      type: "object",
      properties: {
        scale: {
          type: "number",
          description: "Scale factor (default: 1.0)",
          default: 1.0
        },
        filename: {
          type: "string",
          description: "Output filename (default: 'geogebra-export.pdf')",
          default: "geogebra-export.pdf"
        },
        dpi: {
          type: "number",
          description: "DPI resolution (default: 72)",
          default: 72
        }
      }
    }
  },
  {
    name: "set_xml",
    description: "Load a GeoGebra construction from XML content",
    inputSchema: {
      type: "object",
      properties: {
        xml: {
          type: "string",
          description: "GeoGebra XML content"
        }
      },
      required: ["xml"]
    }
  },
  {
    name: "get_xml",
    description: "Get the current GeoGebra construction as XML",
    inputSchema: {
      type: "object",
      properties: {}
    }
  },
  {
    name: "refresh_views",
    description: "Refresh all GeoGebra views to update the display",
    inputSchema: {
      type: "object",
      properties: {}
    }
  },
  {
    name: "math_calculation",
    description: "Perform mathematical calculations using GeoGebra's engine",
    inputSchema: {
      type: "object",
      properties: {
        expression: {
          type: "string",
          description: "Mathematical expression to evaluate"
        },
        variables: {
          type: "object",
          description: "Variable values as key-value pairs"
        }
      },
      required: ["expression"]
    }
  },
  {
    name: "geometry_construction",
    description: "Create geometric constructions and get properties",
    inputSchema: {
      type: "object",
      properties: {
        construction: {
          type: "string",
          description: "Geometric construction commands"
        },
        properties: {
          type: "array",
          description: "Properties to calculate (e.g., ['area', 'perimeter', 'coordinates'])",
          items: { type: "string" }
        }
      },
      required: ["construction"]
    }
  },
  {
    name: "get_coordinates",
    description: "Get coordinates of geometric objects for number-shape analysis",
    inputSchema: {
      type: "object",
      properties: {
        objectName: {
          type: "string",
          description: "Name of the object to get coordinates for"
        }
      },
      required: ["objectName"]
    }
  },
  {
    name: "find_intersections",
    description: "Find intersection points between geometric objects",
    inputSchema: {
      type: "object",
      properties: {
        object1: {
          type: "string",
          description: "First object name or equation"
        },
        object2: {
          type: "string",
          description: "Second object name or equation"
        }
      },
      required: ["object1", "object2"]
    }
  },
  {
    name: "find_tangents",
    description: "Find tangent lines to curves at specific points",
    inputSchema: {
      type: "object",
      properties: {
        curve: {
          type: "string",
          description: "Curve name or equation"
        },
        point: {
          type: "string",
          description: "Point name or coordinates"
        }
      },
      required: ["curve", "point"]
    }
  },
  {
    name: "find_roots_extrema",
    description: "Find roots and extrema of functions",
    inputSchema: {
      type: "object",
      properties: {
        function: {
          type: "string",
          description: "Function name or equation"
        },
        find: {
          type: "string",
          description: "What to find: 'roots', 'extrema', or 'both'",
          enum: ["roots", "extrema", "both"]
        }
      },
      required: ["function", "find"]
    }
  },
  {
    name: "set_viewport",
    description: "Set the coordinate system viewport for optimal visualization",
    inputSchema: {
      type: "object",
      properties: {
        xmin: {
          type: "number",
          description: "Minimum x value"
        },
        xmax: {
          type: "number",
          description: "Maximum x value"
        },
        ymin: {
          type: "number",
          description: "Minimum y value"
        },
        ymax: {
          type: "number",
          description: "Maximum y value"
        }
      },
      required: ["xmin", "xmax", "ymin", "ymax"]
    }
  }
];
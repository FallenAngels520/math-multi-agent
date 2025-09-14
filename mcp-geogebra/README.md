# GeoGebra MCP Server

A Model Context Protocol (MCP) server that provides access to GeoGebra's computation and drawing capabilities through a standardized interface.

## Features

### Computation Tools
- **eval_command**: Execute GeoGebra commands
- **eval_command_cas**: Computer Algebra System calculations
- **math_calculation**: Mathematical expression evaluation
- **geometry_construction**: Geometric constructions and property calculations

### Drawing & Export Tools
- **export_png**: Export constructions as PNG images
- **export_pdf**: Export constructions as PDF documents
- **set_xml**: Load constructions from XML
- **get_xml**: Get current construction as XML
- **refresh_views**: Refresh all views

## Installation

1. Install dependencies:
```bash
cd mcp-geogebra
npm install
```

2. Make the server executable:
```bash
chmod +x src/index.js
```

## Configuration

Add to your MCP client configuration (e.g., for Claude Code):

```json
{
  "mcpServers": {
    "geogebra": {
      "command": "node",
      "args": ["/path/to/mcp-geogebra/src/index.js"],
      "env": {
        "GEOGEBRA_BASE_URL": "http://localhost:3000"
      }
    }
  }
}
```

## Usage Examples

### Basic Math Calculation
```javascript
// Calculate integral of x^2 from 0 to 1
{
  "name": "math_calculation",
  "arguments": {
    "expression": "Integral(x^2, 0, 1)"
  }
}
```

### CAS Calculation
```javascript
// Solve quadratic equation
{
  "name": "eval_command_cas", 
  "arguments": {
    "command": "Solve(x^2 - 4 = 0, x)",
    "rounding": "2"
  }
}
```

### Geometry Construction
```javascript
// Create triangle and get area
{
  "name": "geometry_construction",
  "arguments": {
    "construction": "A=(0,0); B=(4,0); C=(0,3); poly1=Polygon(A,B,C)",
    "properties": ["area", "perimeter"]
  }
}
```

### Export Image
```javascript
// Export as high-quality PNG
{
  "name": "export_png",
  "arguments": {
    "exportScale": 2.0,
    "transparent": true,
    "dpi": 600
  }
}
```

## API Reference

### eval_command
Execute a GeoGebra command.

**Parameters:**
- `command` (string): GeoGebra command to execute

**Example:** `"f(x)=x^2; Integral(f,0,1)"`

### eval_command_cas  
Execute CAS command with precision control.

**Parameters:**
- `command` (string): CAS command
- `rounding` (string): Rounding precision (default: "2")

**Example:** `"Solve(x^3 - 2x + 1 = 0, x)"`

### export_png
Export construction as PNG image.

**Parameters:**
- `exportScale` (number): Scale factor (default: 1.0)
- `transparent` (boolean): Transparent background (default: false)
- `dpi` (number): Resolution (default: 300)
- `greyscale` (boolean): Greyscale output (default: false)

### export_pdf
Export construction as PDF document.

**Parameters:**
- `scale` (number): Scale factor (default: 1.0)
- `filename` (string): Output filename
- `dpi` (number): Resolution (default: 72)

### math_calculation
Evaluate mathematical expressions.

**Parameters:**
- `expression` (string): Math expression
- `variables` (object): Variable values

**Example:** 
```json
{
  "expression": "a^2 + b^2",
  "variables": {"a": 3, "b": 4}
}
```

### geometry_construction
Create geometric constructions and get properties.

**Parameters:**
- `construction` (string): Construction commands
- `properties` (array): Properties to calculate

**Supported properties:** `area`, `perimeter`, `coordinates`

## Environment Variables

- `GEOGEBRA_BASE_URL`: Base URL of GeoGebra server (default: http://localhost:3000)

## Development

### Project Structure
```
mcp-geogebra/
├── src/
│   ├── index.js          # Main server entry point
│   ├── tools.js          # Tool definitions
│   └── geogebra-client.js # GeoGebra API client
├── package.json
└── README.md
```

### Adding New Tools

1. Define tool in `src/tools.js`
2. Add handler method in `src/index.js`
3. Implement client method in `src/geogebra-client.js`

### Testing

Run the server directly:
```bash
npm start
```

## License

MIT License
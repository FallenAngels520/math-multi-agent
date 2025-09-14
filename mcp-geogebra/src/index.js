#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { geogebraTools } from './tools.js';
import { GeoGebraClient } from './geogebra-client.js';

class GeoGebraMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'geogebra-mcp-server',
        version: '1.0.0'
      },
      {
        capabilities: {
          tools: {}
        }
      }
    );
    
    this.geogebraClient = new GeoGebraClient();
    this.setupToolHandlers();
  }

  setupToolHandlers() {
    // Register all tools
    this.server.setRequestHandler('tools/list', async () => ({
      tools: geogebraTools
    }));

    this.server.setRequestHandler('tools/call', async (request) => {
      const { name, arguments: args } = request.params;
      
      try {
        let result;
        
        switch (name) {
          case 'eval_command':
            result = await this.handleEvalCommand(args);
            break;
            
          case 'eval_command_cas':
            result = await this.handleEvalCommandCAS(args);
            break;
            
          case 'export_png':
            result = await this.handleExportPNG(args);
            break;
            
          case 'export_pdf':
            result = await this.handleExportPDF(args);
            break;
            
          case 'set_xml':
            result = await this.handleSetXML(args);
            break;
            
          case 'get_xml':
            result = await this.handleGetXML(args);
            break;
            
          case 'refresh_views':
            result = await this.handleRefreshViews(args);
            break;
            
          case 'math_calculation':
            result = await this.handleMathCalculation(args);
            break;
            
          case 'geometry_construction':
            result = await this.handleGeometryConstruction(args);
            break;
            
          case 'get_coordinates':
            result = await this.handleGetCoordinates(args);
            break;
            
          case 'find_intersections':
            result = await this.handleFindIntersections(args);
            break;
            
          case 'find_tangents':
            result = await this.handleFindTangents(args);
            break;
            
          case 'find_roots_extrema':
            result = await this.handleFindRootsExtrema(args);
            break;
            
          case 'set_viewport':
            result = await this.handleSetViewport(args);
            break;
            
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
        
        return {
          content: [{
            type: 'text',
            text: JSON.stringify(result, null, 2)
          }]
        };
        
      } catch (error) {
        return {
          content: [{
            type: 'text',
            text: `Error: ${error.message}`
          }],
          isError: true
        };
      }
    });
  }

  async handleEvalCommand(args) {
    const { command } = args;
    const response = await this.geogebraClient.evalCommand(command);
    return { 
      success: true, 
      result: response,
      command: command 
    };
  }

  async handleEvalCommandCAS(args) {
    const { command, rounding = '2' } = args;
    const response = await this.geogebraClient.evalCommandCAS(command, rounding);
    return { 
      success: true, 
      result: response,
      command: command,
      rounding: rounding 
    };
  }

  async handleExportPNG(args) {
    const { exportScale = 1.0, transparent = false, dpi = 300, greyscale = false } = args;
    const response = await this.geogebraClient.getPNGBase64({
      exportScale, transparent, dpi, greyscale
    });
    
    return {
      success: true,
      format: 'png',
      base64: response.data,
      metadata: { exportScale, transparent, dpi, greyscale }
    };
  }

  async handleExportPDF(args) {
    const { scale = 1.0, filename = 'geogebra-export.pdf', dpi = 72 } = args;
    const response = await this.geogebraClient.exportPDF({
      scale, filename, dpi
    });
    
    return {
      success: true,
      format: 'pdf',
      filename: filename,
      metadata: { scale, dpi }
    };
  }

  async handleSetXML(args) {
    const { xml } = args;
    const response = await this.geogebraClient.setXML(xml);
    return { 
      success: true, 
      result: response 
    };
  }

  async handleGetXML(args) {
    const response = await this.geogebraClient.getXML();
    return { 
      success: true, 
      xml: response.data 
    };
  }

  async handleRefreshViews(args) {
    const response = await this.geogebraClient.refreshViews();
    return { 
      success: true, 
      result: response 
    };
  }

  async handleMathCalculation(args) {
    const { expression, variables = {} } = args;
    
    // Build GeoGebra command from expression and variables
    let command = expression;
    if (Object.keys(variables).length > 0) {
      const varCommands = Object.entries(variables)
        .map(([varName, value]) => `${varName}=${value}`)
        .join(';');
      command = `${varCommands};${expression}`;
    }
    
    const response = await this.geogebraClient.evalCommand(command);
    return {
      success: true,
      expression: expression,
      variables: variables,
      result: response
    };
  }

  async handleGeometryConstruction(args) {
    const { construction, properties = [] } = args;
    
    // Execute construction commands
    const constructionResponse = await this.geogebraClient.evalCommand(construction);
    
    let results = {};
    
    // Get requested properties
    if (properties.includes('area')) {
      const areaResponse = await this.geogebraClient.evalCommand('Area()');
      results.area = areaResponse;
    }
    
    if (properties.includes('perimeter')) {
      const perimeterResponse = await this.geogebraClient.evalCommand('Perimeter()');
      results.perimeter = perimeterResponse;
    }
    
    if (properties.includes('coordinates')) {
      const coordsResponse = await this.geogebraClient.evalCommand('Coordinates()');
      results.coordinates = coordsResponse;
    }
    
    return {
      success: true,
      construction: construction,
      properties: results,
      rawResponse: constructionResponse
    };
  }

  async handleGetCoordinates(args) {
    const { objectName } = args;
    
    // Use evalCommand to get coordinates through GeoGebra commands
    const xCoordCommand = `x(${objectName})`;
    const yCoordCommand = `y(${objectName})`;
    
    const xResponse = await this.geogebraClient.evalCommand(xCoordCommand);
    const yResponse = await this.geogebraClient.evalCommand(yCoordCommand);
    
    return {
      success: true,
      objectName: objectName,
      coordinates: {
        x: xResponse,
        y: yResponse
      }
    };
  }

  async handleFindIntersections(args) {
    const { object1, object2 } = args;
    
    // Use Intersect command to find intersection points
    const intersectCommand = `Intersect(${object1}, ${object2})`;
    const response = await this.geogebraClient.evalCommand(intersectCommand);
    
    return {
      success: true,
      object1: object1,
      object2: object2,
      intersections: response
    };
  }

  async handleFindTangents(args) {
    const { curve, point } = args;
    
    // Use Tangent command to find tangent line
    const tangentCommand = `Tangent(${curve}, ${point})`;
    const response = await this.geogebraClient.evalCommand(tangentCommand);
    
    return {
      success: true,
      curve: curve,
      point: point,
      tangent: response
    };
  }

  async handleFindRootsExtrema(args) {
    const { function: func, find } = args;
    
    let results = {};
    
    if (find === 'roots' || find === 'both') {
      const rootCommand = `Root(${func})`;
      results.roots = await this.geogebraClient.evalCommand(rootCommand);
    }
    
    if (find === 'extrema' || find === 'both') {
      const extremaCommand = `Extremum(${func})`;
      results.extrema = await this.geogebraClient.evalCommand(extremaCommand);
    }
    
    return {
      success: true,
      function: func,
      find: find,
      results: results
    };
  }

  async handleSetViewport(args) {
    const { xmin, xmax, ymin, ymax } = args;
    
    // Use setCoordSystem command to adjust viewport
    const viewportCommand = `setCoordSystem(${xmin}, ${xmax}, ${ymin}, ${ymax})`;
    const response = await this.geogebraClient.evalCommand(viewportCommand);
    
    return {
      success: true,
      viewport: { xmin, xmax, ymin, ymax },
      result: response
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('GeoGebra MCP Server running on stdio');
  }
}

const server = new GeoGebraMCPServer();
server.run().catch(console.error);
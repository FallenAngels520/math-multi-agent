import fetch from 'node-fetch';

class GeoGebraClient {
  constructor(baseUrl = 'http://localhost:3000') {
    this.baseUrl = baseUrl;
  }

  async evalCommand(command) {
    const response = await fetch(`${this.baseUrl}/evalCommand`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command })
    });
    return response.json();
  }

  async evalCommandCAS(command, rounding = '2') {
    const response = await fetch(`${this.baseUrl}/evalCommandCAS`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command, rounding })
    });
    return response.json();
  }

  async getPNGBase64(options = {}) {
    const {
      exportScale = 1.0,
      transparent = false,
      dpi = 300,
      greyscale = false
    } = options;
    
    const response = await fetch(`${this.baseUrl}/getPNGBase64`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ exportScale, transparent, dpi, greyscale })
    });
    return response.json();
  }

  async exportPDF(options = {}) {
    const {
      scale = 1.0,
      filename = 'geogebra-export.pdf',
      dpi = 72
    } = options;
    
    const response = await fetch(`${this.baseUrl}/exportPDF`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scale, filename, dpi })
    });
    return response.json();
  }

  async setXML(xmlContent) {
    const response = await fetch(`${this.baseUrl}/setXML`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ xml: xmlContent })
    });
    return response.json();
  }

  async getXML() {
    const response = await fetch(`${this.baseUrl}/getXML`);
    return response.json();
  }

  async refreshViews() {
    const response = await fetch(`${this.baseUrl}/refreshViews`, {
      method: 'POST'
    });
    return response.json();
  }
}
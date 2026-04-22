# AbletonMCP Documentation

Welcome to the AbletonMCP documentation. This documentation provides comprehensive technical reference for the Ableton Live Model Context Protocol integration.

## Project Overview

AbletonMCP connects AI assistants (Claude Desktop, Cursor) to Ableton Live through the Model Context Protocol (MCP), enabling prompt-assisted music production and session manipulation.

## Documentation Structure

```
doc/
├── README.md              # This file
├── architecture/          # System design and architecture
│   ├── overview.md       # High-level architecture
│   ├── components.md     # Component descriptions
│   └── data-flow.md     # Data and control flow
├── features/             # Feature documentation
│   ├── session-management.md
│   ├── track-management.md
│   ├── clip-management.md
│   ├── transport-control.md
│   └── browser-navigation.md
├── api/                 # API documentation
│   ├── endpoints.md     # MCP tool endpoints
│   └── contracts.md      # Request/response formats
├── setup/               # Installation guides
│   ├── installation.md  # Installation instructions
│   └── configuration.md # Configuration reference
└── development/         # Development guides
    ├── workflow.md      # Development workflow
    └── testing.md      # Testing guide
```

## Quick Links

- [Architecture Overview](architecture/overview.md)
- [MCP Endpoints](api/endpoints.md)
- [Installation Guide](setup/installation.md)

## Prerequisites

- Ableton Live 10 or newer
- Python 3.10 or newer
- uv package manager
- Claude Desktop or Cursor with MCP support
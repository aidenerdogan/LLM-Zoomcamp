# mcp_client.py

import subprocess
import json
import time

class MCPClient:
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    def start_server(self):
        self.process = subprocess.Popen(
            self.cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

    def _send_json(self, obj):
        json_str = json.dumps(obj) + '\n'
        self.process.stdin.write(json_str)
        self.process.stdin.flush()
        return json_str.strip()

    def _read_json(self):
        while True:
            line = self.process.stdout.readline()
            if not line:
                continue
            line = line.strip()
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                # Skip banners or non-JSON lines
                continue

    def initialize(self):
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        self._send_json(request)
        return self._read_json()

    def initialized(self):
        self._send_json({
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        })

    def get_tools(self):
        self._send_json({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        })
        return self._read_json()["result"]

    def call_tool(self, name, arguments):
        self._send_json({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments
            }
        })
        return self._read_json()["result"]
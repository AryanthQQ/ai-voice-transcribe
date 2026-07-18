import sys
import os
from pathlib import Path
sys.path.append(str(Path('backend').resolve()))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get('/health')
    assert response.status_code == 200
    data = response.json()
    
    # Assert specific required fields are present
    assert "active_pipeline" in data
    assert "primary_stt_model" in data
    assert "fallback_stt_model" in data
    
    modules = data["modules"]
    assert "stt_loaded" in modules
    assert "contact_engine_loaded" in modules
    assert "compliance_engine_loaded" in modules
    
    system = data["system"]
    assert "cpu_percent" in system
    assert "ram_percent" in system
    assert "disk_percent" in system
    
    deps = data["dependencies"]
    assert "ffprobe_available" in deps
    assert "temp_dir_writable" in deps

test_health_endpoint()
print('Observability verification passed.')

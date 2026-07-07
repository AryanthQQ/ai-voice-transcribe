import traceback
try:
    from app.core.config import settings
    from app.main import app
    print("SUCCESS")
    print(settings.BASE_DIR)
except Exception as e:
    print("FAILED")
    traceback.print_exc()

# coupon_checker/middleware/request_logger.py

import traceback
from datetime import datetime

class SimpleRequestLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        method = request.method
        path = request.get_full_path()
        ip = request.META.get("REMOTE_ADDR", "unknown")
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"\n🔵 [REQUEST] {time}")
        print(f"   IP: {ip}")
        print(f"   Method: {method}")
        print(f"   Path: {path}")

        try:
            response = self.get_response(request)
        except Exception as e:
            print(f"🔴 [EXCEPTION] {method} {path}")
            print(f"   Error: {str(e)}")
            traceback.print_exc()
            raise

        status = response.status_code
        status_color = "🟢" if status < 400 else "🟠" if status < 500 else "🔴"

        print(f"{status_color} [RESPONSE] Status: {status}")
        return response

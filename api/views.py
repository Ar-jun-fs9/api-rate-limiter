from .rate_limit import RateLimitedAPIView, RateLimited10APIView



class TestAPIView(RateLimited10APIView):
    def get(self, request):
        return self.handle_request(request, message="Test API Success")


class HelloAPIView(RateLimited10APIView):
    def get(self, request):
        return self.handle_request(request, message="Hello API Success")


class ProfileAPIView(RateLimited10APIView):
    def get(self, request):
        return self.handle_request(request, message="Profile API Success")


class LoginAPIView(RateLimitedAPIView):
    max_requests = 20
    def get(self, request):
        return self.handle_request(request, message="Login API Success")


class PurchaseAPIView(RateLimitedAPIView):
    max_requests = 15
    def get(self, request):
        return self.handle_request(request, message="Purchase API Success")
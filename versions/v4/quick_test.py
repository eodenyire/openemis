import urllib.request
try:
    with urllib.request.urlopen("http://127.0.0.1:8000/", timeout=3) as response:
        print(f"✅ Status: {response.getcode()}")
        print("🎉 Server is working!")
except Exception as e:
    print(f"❌ Error: {e}")
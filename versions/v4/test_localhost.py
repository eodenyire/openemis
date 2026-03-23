import urllib.request
try:
    with urllib.request.urlopen("http://localhost:8000/", timeout=3) as response:
        print(f"✅ Status: {response.getcode()}")
        print("🎉 Server is working on localhost!")
except Exception as e:
    print(f"❌ Error: {e}")
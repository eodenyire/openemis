#!/usr/bin/env python3
import urllib.request
import urllib.error

def test_server():
    url = "http://127.0.0.1:8001/"
    
    try:
        print("🔍 Testing server on port 8001...")
        
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'Test Script')
        
        with urllib.request.urlopen(request, timeout=5) as response:
            status_code = response.getcode()
            content = response.read().decode('utf-8')[:200]  # First 200 chars
            
            print(f"✅ Server is responding!")
            print(f"   Status Code: {status_code}")
            print(f"   Content preview: {content}...")
            
            return True
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == '__main__':
    test_server()
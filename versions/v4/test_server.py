#!/usr/bin/env python3
"""
Test script to check if the Django server is responding
"""
import urllib.request
import urllib.error
import sys

def test_server():
    """Test if the server is responding"""
    url = "http://127.0.0.1:8000/"
    
    try:
        print("🔍 Testing server connection...")
        
        # Create a request with a timeout
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'Test Script')
        
        with urllib.request.urlopen(request, timeout=10) as response:
            status_code = response.getcode()
            content_type = response.headers.get('Content-Type', 'Unknown')
            content_length = len(response.read())
            
            print(f"✅ Server is responding!")
            print(f"   Status Code: {status_code}")
            print(f"   Content Type: {content_type}")
            print(f"   Content Length: {content_length} bytes")
            
            if status_code == 200:
                print("🎉 Server is working correctly!")
                return True
            else:
                print(f"⚠️  Server returned status code: {status_code}")
                return False
                
    except urllib.error.URLError as e:
        print(f"❌ Connection failed: {e}")
        print("   Possible causes:")
        print("   - Server is not running")
        print("   - Server is starting up")
        print("   - Port 8000 is blocked")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_admin():
    """Test if the admin panel is accessible"""
    url = "http://127.0.0.1:8000/admin/"
    
    try:
        print("\n🔍 Testing admin panel...")
        
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'Test Script')
        
        with urllib.request.urlopen(request, timeout=10) as response:
            status_code = response.getcode()
            print(f"✅ Admin panel is accessible!")
            print(f"   Status Code: {status_code}")
            return True
            
    except Exception as e:
        print(f"❌ Admin panel test failed: {e}")
        return False

if __name__ == '__main__':
    print("🎓 School Management System - Server Test")
    print("=" * 50)
    
    # Test main server
    main_ok = test_server()
    
    # Test admin panel
    admin_ok = test_admin()
    
    print("\n" + "=" * 50)
    if main_ok and admin_ok:
        print("🎉 All tests passed! Server is working correctly.")
        print("\n📍 You can access:")
        print("   • Main site: http://127.0.0.1:8000")
        print("   • Admin panel: http://127.0.0.1:8000/admin")
        print("\n🔑 Login credentials:")
        print("   • Username: admin")
        print("   • Password: admin123")
    else:
        print("❌ Some tests failed. Please check the server status.")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure the server is running: python manage.py runserver")
        print("   2. Check if port 8000 is available")
        print("   3. Verify firewall settings")
        print("   4. Try accessing http://localhost:8000 instead")
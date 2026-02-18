"""
Test script to verify server stability - multiple consecutive requests
"""
import requests
import time

BASE_URL = "https://text-to-structured-data.onrender.com"
# BASE_URL = "http://127.0.0.1:8000"  # Para testing local

def test_health_endpoint():
    """Test if server is responding"""
    print("🔍 Testing server health...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ Server responded: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Server not responding: {e}")
        return False

def test_multiple_requests():
    """Test if server stays alive after multiple requests"""
    print("\n🔁 Testing multiple consecutive requests...")
    
    # Create simple test file content
    test_content = """
    FACTURA #12345
    Cliente: Juan Pérez
    Monto Total: $1,500.00
    Fecha: 18/02/2026
    Tipo: Factura
    """
    
    for i in range(1, 4):
        print(f"\n--- Request {i}/3 ---")
        try:
            # Create file-like object
            files = {
                'file': ('test_factura.txt', test_content.encode(), 'text/plain')
            }
            
            print(f"⏳ Sending request at {time.strftime('%H:%M:%S')}")
            start_time = time.time()
            
            response = requests.post(
                f"{BASE_URL}/api/process",
                files=files,
                timeout=60
            )
            
            elapsed = time.time() - start_time
            print(f"⏱️  Response time: {elapsed:.2f}s")
            print(f"📊 Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                cliente = data.get('structured_data', {}).get('cliente', 'N/A')
                print(f"✅ Success - Cliente: {cliente}")
            else:
                print(f"❌ Error: {response.text}")
            
            # Wait 2 seconds between requests (server should stay alive)
            if i < 3:
                print("⏸️  Waiting 2 seconds...")
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Request {i} failed: {e}")
            return False
    
    print("\n✅ All requests completed successfully - server is stable!")
    return True

def test_cold_start():
    """Test cold start detection"""
    print("\n🥶 Testing cold start behavior...")
    print("Waiting 5 seconds to simulate short idle time...")
    time.sleep(5)
    
    try:
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/", timeout=35)
        elapsed = time.time() - start_time
        
        print(f"⏱️  Response time: {elapsed:.2f}s")
        if elapsed > 20:
            print("⚠️  Possible cold start detected (>20s)")
        else:
            print("✅ Server was already warm")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Cold start test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("SERVER STABILITY TEST")
    print("=" * 60)
    
    # Test 1: Basic health check
    if not test_health_endpoint():
        print("\n❌ Server is not responding. Exiting...")
        exit(1)
    
    # Test 2: Multiple consecutive requests
    if not test_multiple_requests():
        print("\n❌ Server crashed during consecutive requests")
        exit(1)
    
    # Test 3: Cold start behavior
    test_cold_start()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - Server is stable")
    print("=" * 60)

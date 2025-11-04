#!/usr/bin/env python3
"""
Test script for ConvertKeylogApp Geometry API
Demonstrates all major API endpoints and functionality
"""

import requests
import json
import time

# API base URL
BASE_URL = 'http://localhost:5000'

def test_health_check():
    """Test API health check endpoint"""
    print("🏥 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/")
        result = response.json()
        print(f"✅ Status: {result['status']}")
        print(f"📋 Available endpoints: {len(result['available_endpoints'])}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_get_shapes():
    """Test getting available shapes"""
    print("\n🔺 Testing get shapes...")
    try:
        response = requests.get(f"{BASE_URL}/api/geometry/shapes")
        result = response.json()
        print(f"✅ Available shapes: {result['data']}")
        return result['data']
    except Exception as e:
        print(f"❌ Get shapes failed: {e}")
        return []

def test_get_operations():
    """Test getting available operations"""
    print("\n⚡ Testing get operations...")
    try:
        response = requests.get(f"{BASE_URL}/api/geometry/operations")
        result = response.json()
        print(f"✅ Available operations: {result['data']}")
        return result['data']
    except Exception as e:
        print(f"❌ Get operations failed: {e}")
        return []

def test_shapes_for_operation():
    """Test getting shapes for specific operation"""
    print("\n🔍 Testing shapes for operation...")
    operation = "Khoảng cách"
    try:
        response = requests.get(f"{BASE_URL}/api/geometry/operations/{operation}/shapes")
        result = response.json()
        print(f"✅ Shapes for '{operation}': {result['data']}")
        return True
    except Exception as e:
        print(f"❌ Get shapes for operation failed: {e}")
        return False

def test_get_template():
    """Test getting input templates"""
    print("\n📝 Testing get template...")
    try:
        # Single shape template
        response = requests.get(f"{BASE_URL}/api/geometry/template/Điểm")
        result = response.json()
        print(f"✅ Template for Điểm:")
        print(json.dumps(result['template'], indent=2, ensure_ascii=False))
        
        # Dual shape template
        response = requests.get(f"{BASE_URL}/api/geometry/template/Điểm/Đường thẳng")
        result = response.json()
        print(f"\n✅ Template for Điểm + Đường thẳng: OK")
        return True
    except Exception as e:
        print(f"❌ Get template failed: {e}")
        return False

def test_validate_input():
    """Test input validation"""
    print("\n✅ Testing input validation...")
    
    # Valid input
    valid_data = {
        "operation": "Khoảng cách",
        "shape_A": "Điểm",
        "data_A": {
            "point_input": "1,2,3"
        },
        "shape_B": "Điểm", 
        "data_B": {
            "point_input": "4,5,6"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/geometry/validate", json=valid_data)
        result = response.json()
        print(f"✅ Valid input validation: {result['validation']['valid']}")
        
        # Invalid input
        invalid_data = {
            "operation": "Invalid Operation",
            "shape_A": "Điểm"
        }
        
        response = requests.post(f"{BASE_URL}/api/geometry/validate", json=invalid_data)
        result = response.json()
        validation = result['validation']
        print(f"❌ Invalid input validation: {validation['valid']}")
        print(f"   Errors: {validation['errors']}")
        
        return True
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False

def test_single_processing():
    """Test single geometry processing"""
    print("\n🧮 Testing single processing...")
    
    test_cases = [
        {
            "name": "Distance between two points",
            "data": {
                "operation": "Khoảng cách",
                "shape_A": "Điểm",
                "data_A": {"point_input": "1,2,3"},
                "shape_B": "Điểm", 
                "data_B": {"point_input": "4,5,6"},
                "dimension_A": "3",
                "dimension_B": "3"
            }
        },
        {
            "name": "Circle area",
            "data": {
                "operation": "Diện tích",
                "shape_A": "Đường tròn",
                "data_A": {
                    "circle_center": "0,0",
                    "circle_radius": "sqrt(5)"
                }
            }
        },
        {
            "name": "Sphere volume", 
            "data": {
                "operation": "Thể tích",
                "shape_A": "Mặt cầu",
                "data_A": {
                    "sphere_center": "0,0,0",
                    "sphere_radius": "3"
                }
            }
        },
        {
            "name": "Line intersection",
            "data": {
                "operation": "Tương giao",
                "shape_A": "Đường thẳng",
                "data_A": {
                    "line_A1": "0,0,0",
                    "line_X1": "1,1,1"
                },
                "shape_B": "Mặt phẳng",
                "data_B": {
                    "plane_a": "1",
                    "plane_b": "1", 
                    "plane_c": "1",
                    "plane_d": "0"
                }
            }
        }
    ]
    
    success_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            print(f"\n  Test {i}: {test_case['name']}")
            response = requests.post(f"{BASE_URL}/api/geometry/process", json=test_case['data'])
            
            if response.status_code == 200:
                result = response.json()
                data = result['data']
                print(f"  ✅ Operation: {data['operation']}")
                print(f"  🔑 Keylog: {data['keylog']}")
                print(f"  📊 Encoded A: {data['encoded_A']}")
                if data['encoded_B']:
                    print(f"  📊 Encoded B: {data['encoded_B']}")
                success_count += 1
            else:
                print(f"  ❌ HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"  ❌ Test failed: {e}")
    
    print(f"\n📊 Single processing results: {success_count}/{len(test_cases)} tests passed")
    return success_count == len(test_cases)

def test_batch_processing():
    """Test batch processing"""
    print("\n📦 Testing batch processing...")
    
    batch_data = {
        "calculations": [
            {
                "operation": "Diện tích",
                "shape_A": "Đường tròn", 
                "data_A": {
                    "circle_center": "0,0",
                    "circle_radius": "5"
                }
            },
            {
                "operation": "Thể tích",
                "shape_A": "Mặt cầu",
                "data_A": {
                    "sphere_center": "0,0,0",
                    "sphere_radius": "2"
                }
            },
            {
                "operation": "Khoảng cách",
                "shape_A": "Điểm",
                "data_A": {"point_input": "0,0,0"},
                "shape_B": "Điểm",
                "data_B": {"point_input": "3,4,0"},
                "dimension_A": "3",
                "dimension_B": "3"
            },
            {
                # Invalid calculation to test error handling
                "operation": "Invalid",
                "shape_A": "Unknown"
            }
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/geometry/batch", json=batch_data)
        result = response.json()
        
        print(f"✅ Batch processed: {result['total_processed']} calculations")
        
        success_count = 0
        error_count = 0
        
        for item in result['data']:
            index = item['index']
            status = item['status']
            
            if status == 'success':
                print(f"  ✅ Calculation {index + 1}: {item['keylog']}")
                success_count += 1
            else:
                print(f"  ❌ Calculation {index + 1}: {item.get('message', item.get('errors', 'Unknown error'))}")
                error_count += 1
        
        print(f"📊 Batch results: {success_count} success, {error_count} errors")
        return True
        
    except Exception as e:
        print(f"❌ Batch processing failed: {e}")
        return False

def test_error_handling():
    """Test API error handling"""
    print("\n🚨 Testing error handling...")
    
    # Test 404
    try:
        response = requests.get(f"{BASE_URL}/api/nonexistent")
        print(f"✅ 404 handling: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 404 test failed: {e}")
    
    # Test invalid JSON
    try:
        response = requests.post(
            f"{BASE_URL}/api/geometry/process",
            data="invalid json",
            headers={'Content-Type': 'application/json'}
        )
        print(f"✅ Invalid JSON handling: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Invalid JSON test failed: {e}")
    
    # Test missing required fields
    try:
        response = requests.post(f"{BASE_URL}/api/geometry/process", json={})
        result = response.json()
        print(f"✅ Missing fields handling: {result['message']}")
    except Exception as e:
        print(f"❌ Missing fields test failed: {e}")
    
    return True

def main():
    """Run all tests"""
    print("🚀 ConvertKeylogApp Geometry API Test Suite")
    print("=" * 50)
    
    # Check if API is running
    if not test_health_check():
        print("\n❌ API is not running. Please start the API server first:")
        print("   python app.py")
        return
    
    time.sleep(0.5)
    
    # Run all tests
    tests = [
        test_get_shapes,
        test_get_operations, 
        test_shapes_for_operation,
        test_get_template,
        test_validate_input,
        test_single_processing,
        test_batch_processing,
        test_error_handling
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        time.sleep(0.3)
    
    print("\n" + "=" * 50)
    print(f"🏁 Test Suite Complete: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the API implementation.")

if __name__ == '__main__':
    main()
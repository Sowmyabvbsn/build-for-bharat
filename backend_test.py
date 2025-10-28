import requests
import sys
import json
from datetime import datetime

class MGNREGAAPITester:
    def __init__(self, base_url="https://mgnrega-insights-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                    elif isinstance(response_data, dict):
                        print(f"   Response keys: {list(response_data.keys())}")
                except:
                    print(f"   Response: {response.text[:100]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                self.failed_tests.append({
                    "test": name,
                    "expected": expected_status,
                    "actual": response.status_code,
                    "response": response.text[:200]
                })

            return success, response.json() if success and response.text else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append({
                "test": name,
                "error": str(e)
            })
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API", "GET", "", 200)

    def test_get_districts(self):
        """Test getting all districts"""
        success, response = self.run_test("Get All Districts", "GET", "districts", 200)
        if success and isinstance(response, list):
            print(f"   Found {len(response)} districts")
            if len(response) > 0:
                print(f"   Sample district: {response[0].get('name', 'N/A')} ({response[0].get('code', 'N/A')})")
        return success, response

    def test_state_overview(self):
        """Test state overview endpoint"""
        success, response = self.run_test("State Overview", "GET", "state/overview", 200)
        if success:
            print(f"   Total districts: {response.get('total_districts', 'N/A')}")
            print(f"   Total active workers: {response.get('total_active_workers', 'N/A')}")
        return success, response

    def test_district_current_data(self, district_code="UP001"):
        """Test getting current data for a district"""
        success, response = self.run_test(
            f"District Current Data ({district_code})", 
            "GET", 
            f"districts/{district_code}/current", 
            200
        )
        if success:
            print(f"   District: {response.get('district_name', 'N/A')}")
            print(f"   Performance Grade: {response.get('performance_grade', 'N/A')}")
        return success, response

    def test_district_trends(self, district_code="UP001"):
        """Test getting trends for a district"""
        success, response = self.run_test(
            f"District Trends ({district_code})", 
            "GET", 
            f"districts/{district_code}/trends", 
            200,
            params={"months": 6}
        )
        if success:
            trends = response.get('trends', [])
            print(f"   Trends data points: {len(trends)}")
        return success, response

    def test_districts_compare(self):
        """Test comparing multiple districts"""
        success, response = self.run_test(
            "Compare Districts", 
            "GET", 
            "districts/compare", 
            200,
            params={"codes": "UP001,UP002,UP003"}
        )
        if success:
            comparisons = response.get('comparisons', [])
            print(f"   Comparison data for {len(comparisons)} districts")
        return success, response

    def test_location_detect(self):
        """Test location detection endpoint"""
        # Test with sample coordinates (Lucknow, UP)
        test_location = {
            "latitude": 26.8467,
            "longitude": 80.9462
        }
        success, response = self.run_test(
            "Location Detection", 
            "POST", 
            "location/detect", 
            200,
            data=test_location
        )
        if success:
            print(f"   Detection success: {response.get('success', 'N/A')}")
            if response.get('success'):
                district = response.get('district', {})
                print(f"   Detected district: {district.get('name', 'N/A')}")
        return success, response

    def test_invalid_district(self):
        """Test with invalid district code"""
        success, response = self.run_test(
            "Invalid District Code", 
            "GET", 
            "districts/INVALID/current", 
            404
        )
        return success, response

def main():
    print("🚀 Starting MGNREGA API Testing...")
    print("=" * 50)
    
    tester = MGNREGAAPITester()
    
    # Run all tests
    print("\n📋 Testing Core Endpoints...")
    tester.test_root_endpoint()
    
    print("\n🏛️ Testing Districts Endpoints...")
    districts_success, districts_data = tester.test_get_districts()
    
    print("\n📊 Testing State Overview...")
    tester.test_state_overview()
    
    # Test with first district if available
    test_district = "UP001"
    if districts_success and districts_data and len(districts_data) > 0:
        test_district = districts_data[0].get('code', 'UP001')
    
    print(f"\n🎯 Testing District-Specific Endpoints (using {test_district})...")
    tester.test_district_current_data(test_district)
    tester.test_district_trends(test_district)
    
    print("\n🔄 Testing Comparison Endpoint...")
    tester.test_districts_compare()
    
    print("\n📍 Testing Location Detection...")
    tester.test_location_detect()
    
    print("\n❌ Testing Error Handling...")
    tester.test_invalid_district()
    
    # Print final results
    print("\n" + "=" * 50)
    print("📊 FINAL RESULTS")
    print("=" * 50)
    print(f"✅ Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"❌ Tests failed: {len(tester.failed_tests)}")
    
    if tester.failed_tests:
        print("\n🚨 Failed Tests Details:")
        for i, failure in enumerate(tester.failed_tests, 1):
            print(f"{i}. {failure.get('test', 'Unknown')}")
            if 'error' in failure:
                print(f"   Error: {failure['error']}")
            else:
                print(f"   Expected: {failure.get('expected')}, Got: {failure.get('actual')}")
                print(f"   Response: {failure.get('response', 'N/A')}")
    
    success_rate = (tester.tests_passed / tester.tests_run) * 100 if tester.tests_run > 0 else 0
    print(f"\n🎯 Success Rate: {success_rate:.1f}%")
    
    return 0 if success_rate >= 80 else 1

if __name__ == "__main__":
    sys.exit(main())
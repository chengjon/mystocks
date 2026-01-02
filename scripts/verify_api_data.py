#!/usr/bin/env python3
"""
Analyze API responses for industries, concepts, and stocks data
"""

import json
import subprocess
from datetime import datetime


def get_api_data(endpoint, token):
    """Fetch data from API endpoint"""
    cmd = ["curl", "-s", f"http://localhost:8000{endpoint}", "-H", f"Authorization: Bearer {token}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)


def analyze_industries(data):
    """Analyze industries data"""
    industries = data.get("data", [])
    return {
        "endpoint": "/api/v1/data/stocks/industries",
        "success": data.get("success", False),
        "total_count": len(industries),
        "sample_records": industries[:3],
        "field_names": list(industries[0].keys()) if industries else [],
    }


def analyze_concepts(data):
    """Analyze concepts data"""
    concepts = data.get("data", [])
    total = data.get("total", len(concepts))
    return {
        "endpoint": "/api/v1/data/stocks/concepts",
        "success": data.get("success", False),
        "total_count": total,
        "returned_count": len(concepts),
        "sample_records": concepts[:3],
        "field_names": list(concepts[0].keys()) if concepts else [],
    }


def analyze_stocks(data):
    """Analyze stocks/basic data"""
    stocks = data.get("data", [])
    total = data.get("total", 0)
    limit = data.get("limit", 0)
    return {
        "endpoint": "/api/v1/data/stocks/basic",
        "success": data.get("success", False),
        "total_available": total,
        "returned_count": len(stocks),
        "limit_applied": limit,
        "sample_records": stocks[:3],
        "field_names": list(stocks[0].keys()) if stocks else [],
    }


def main():
    # Get fresh token
    print("🔐 Getting authentication token...")
    token_response = subprocess.run(
        [
            "curl",
            "-s",
            "-X",
            "POST",
            "http://localhost:8000/api/v1/auth/login",
            "-H",
            "Content-Type: application/x-www-form-urlencoded",
            "-d",
            "username=admin&password=admin123",
        ],
        capture_output=True,
        text=True,
    )
    token_data = json.loads(token_response.stdout)
    token = token_data.get("data", {}).get("token", "")
    print(f"✅ Token obtained: {token[:50]}...\n")

    # Fetch data from all endpoints
    print("📊 Fetching data from API endpoints...")

    industries_data = get_api_data("/api/v1/data/stocks/industries", token)
    concepts_data = get_api_data("/api/v1/data/stocks/concepts", token)
    stocks_data = get_api_data("/api/v1/data/stocks/basic?limit=10", token)

    # Analyze each dataset
    print("🔍 Analyzing data...\n")

    industries_analysis = analyze_industries(industries_data)
    concepts_analysis = analyze_concepts(concepts_data)
    stocks_analysis = analyze_stocks(stocks_data)

    # Build report
    report = {
        "timestamp": datetime.now().isoformat(),
        "authentication": {
            "status": "success" if token else "failed",
            "token_type": "JWT Bearer",
            "login_endpoint": "/api/v1/auth/login",
        },
        "endpoints": {
            "industries": industries_analysis,
            "concepts": concepts_analysis,
            "stocks_basic": stocks_analysis,
        },
        "summary": {
            "total_endpoints_tested": 3,
            "successful_endpoints": sum(
                [industries_analysis["success"], concepts_analysis["success"], stocks_analysis["success"]]
            ),
            "data_availability": {
                "industries": f"{industries_analysis['total_count']} records",
                "concepts": f"{concepts_analysis['total_count']} records",
                "stocks": f"{stocks_analysis['total_available']} records available, {stocks_analysis['returned_count']} returned",
            },
        },
        "comparison_with_requirements": {
            "industries": {
                "required": "50+",
                "actual": industries_analysis["total_count"],
                "status": "✅ PASS" if industries_analysis["total_count"] >= 50 else "❌ FAIL",
            },
            "concepts": {
                "required": "100+",
                "actual": concepts_analysis["total_count"],
                "status": "✅ PASS" if concepts_analysis["total_count"] >= 100 else "❌ FAIL",
            },
            "stocks": {
                "required": "4000+",
                "actual": stocks_analysis["total_available"],
                "status": "✅ PASS" if stocks_analysis["total_available"] >= 4000 else "❌ FAIL",
            },
        },
    }

    # Print report
    print("=" * 80)
    print("API VERIFICATION REPORT")
    print("=" * 80)
    print(f"\n📅 Timestamp: {report['timestamp']}")
    print(f"\n🔐 Authentication: {report['authentication']['status'].upper()}")
    print(f"   - Login Endpoint: {report['authentication']['login_endpoint']}")
    print(f"   - Token Type: {report['authentication']['token_type']}")

    print(f"\n📊 Endpoints Tested: {report['summary']['total_endpoints_tested']}")
    print(f"✅ Successful: {report['summary']['successful_endpoints']}/{report['summary']['total_endpoints_tested']}")

    print("\n" + "=" * 80)
    print("INDUSTRIES DATA")
    print("=" * 80)
    print(f"   Endpoint: {industries_analysis['endpoint']}")
    print(f"   Status: {'✅ SUCCESS' if industries_analysis['success'] else '❌ FAILED'}")
    print(f"   Total Records: {industries_analysis['total_count']}")
    print(f"   Fields: {', '.join(industries_analysis['field_names'])}")
    print("\n   Sample Records:")
    for i, record in enumerate(industries_analysis["sample_records"], 1):
        print(f"     {i}. {record}")

    print("\n" + "=" * 80)
    print("CONCEPTS DATA")
    print("=" * 80)
    print(f"   Endpoint: {concepts_analysis['endpoint']}")
    print(f"   Status: {'✅ SUCCESS' if concepts_analysis['success'] else '❌ FAILED'}")
    print(f"   Total Records: {concepts_analysis['total_count']}")
    print(f"   Returned: {concepts_analysis['returned_count']}")
    print(f"   Fields: {', '.join(concepts_analysis['field_names'])}")
    print("\n   Sample Records:")
    for i, record in enumerate(concepts_analysis["sample_records"], 1):
        print(f"     {i}. {record}")

    print("\n" + "=" * 80)
    print("STOCKS BASIC DATA")
    print("=" * 80)
    print(f"   Endpoint: {stocks_analysis['endpoint']}")
    print(f"   Status: {'✅ SUCCESS' if stocks_analysis['success'] else '❌ FAILED'}")
    print(f"   Total Available: {stocks_analysis['total_available']}")
    print(f"   Returned: {stocks_analysis['returned_count']}")
    print(f"   Limit Applied: {stocks_analysis['limit_applied']}")
    print(f"   Fields: {', '.join(stocks_analysis['field_names'])}")
    print("\n   Sample Records:")
    for i, record in enumerate(stocks_analysis["sample_records"], 1):
        print(f"     {i}. {record}")

    print("\n" + "=" * 80)
    print("REQUIREMENTS VERIFICATION")
    print("=" * 80)
    for category, data in report["comparison_with_requirements"].items():
        print(f"\n{category.upper()}:")
        print(f"   Required: {data['required']}")
        print(f"   Actual: {data['actual']}")
        print(f"   Status: {data['status']}")

    print("\n" + "=" * 80)
    print("OVERALL STATUS")
    print("=" * 80)
    all_pass = all(data["status"] == "✅ PASS" for data in report["comparison_with_requirements"].values())
    if all_pass:
        print("✅ ALL REQUIREMENTS MET - API VERIFICATION PASSED")
    else:
        print("❌ SOME REQUIREMENTS NOT MET - API VERIFICATION FAILED")
    print("=" * 80)

    # Save report to file
    report_file = "/opt/claude/mystocks_spec/docs/reports/API_DATA_VERIFICATION_REPORT.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n📄 Report saved to: {report_file}")


if __name__ == "__main__":
    main()

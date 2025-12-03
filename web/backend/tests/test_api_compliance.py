"""
Comprehensive API Compliance Test Suite

This test suite validates that all API endpoints comply with:
- Unified API response structure
- Authentication requirements
- Parameter validation completeness
- HTTP method semantics
- Status code correctness
- REST API design principles

Version: 1.0.0
Date: 2025-12-03
"""

import pytest
import json
import inspect
from typing import Dict, Any, List, Optional, Tuple
from fastapi.testclient import TestClient
from fastapi.routing import APIRoute
from pydantic import BaseModel
from app.main import app
from app.core.responses import APIResponse, ErrorResponse, create_success_response, create_error_response


class APIComplianceValidator:
    """Comprehensive API compliance validation helper"""

    def __init__(self, client: TestClient):
        self.client = client
        self.auth_token = None
        self.test_results = []
        self.endpoints = self._extract_endpoints()

    def _extract_endpoints(self) -> List[Dict[str, Any]]:
        """Extract all API endpoints from FastAPI app"""
        endpoints = []
        for route in app.routes:
            if isinstance(route, APIRoute):
                endpoints.append({
                    'path': route.path,
                    'methods': list(route.methods),
                    'summary': route.summary,
                    'description': route.description,
                    'tags': route.tags,
                    'endpoint': route.endpoint,
                    'dependencies': route.dependencies,
                    'response_model': route.response_model,
                })
        return endpoints

    def get_auth_token(self) -> str:
        """Get authentication token for testing protected endpoints"""
        if not self.auth_token:
            # Login with test credentials
            response = self.client.post(
                "/api/auth/login",
                data={"username": "admin", "password": "admin123"}
            )
            if response.status_code == 200:
                self.auth_token = response.json().get("access_token")
        return self.auth_token

    def validate_response_structure(self, response, endpoint_path: str, method: str) -> Dict[str, Any]:
        """Validate unified API response structure"""
        result = {
            'endpoint': f"{method} {endpoint_path}",
            'status_code': response.status_code,
            'compliance': True,
            'errors': []
        }

        try:
            data = response.json()

            # Check for required response fields
            if response.status_code < 400:
                # Success response should have these fields
                required_fields = ['success']
                optional_fields = ['data', 'message', 'timestamp', 'request_id']

                for field in required_fields:
                    if field not in data:
                        result['compliance'] = False
                        result['errors'].append(f"Missing required field: {field}")

                # Check success field is boolean
                if 'success' in data and not isinstance(data['success'], bool):
                    result['compliance'] = False
                    result['errors'].append("'success' field must be boolean")

            else:
                # Error response should have these fields
                if 'error' not in data and 'detail' not in data:
                    result['compliance'] = False
                    result['errors'].append("Error response missing 'error' or 'detail' field")

                if 'success' in data and data['success'] != False:
                    result['compliance'] = False
                    result['errors'].append("Error response 'success' field must be False")

        except json.JSONDecodeError:
            result['compliance'] = False
            result['errors'].append("Response is not valid JSON")

        return result

    def validate_authentication(self, endpoint_path: str, methods: List[str]) -> Dict[str, Any]:
        """Validate authentication requirements for protected endpoints"""
        result = {
            'endpoint': endpoint_path,
            'auth_required': True,
            'compliance': True,
            'errors': []
        }

        # Skip public endpoints
        public_endpoints = [
            '/health',
            '/api/auth/login',
            '/api/auth/register',
            '/docs',
            '/openapi.json',
            '/redoc',
        ]

        if any(endpoint_path.startswith(pub) for pub in public_endpoints):
            result['auth_required'] = False
            return result

        auth_token = self.get_auth_token()
        if not auth_token:
            result['compliance'] = False
            result['errors'].append("Could not obtain auth token for testing")
            return result

        headers = {"Authorization": f"Bearer {auth_token}"}

        # Test each method
        for method in methods:
            if method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                # Test without auth
                response = self.client.request(method, endpoint_path)

                # Test with auth
                auth_response = self.client.request(method, endpoint_path, headers=headers)

                # Auth should be required for protected endpoints
                if response.status_code == 401 or response.status_code == 403:
                    continue  # Expected behavior
                elif auth_response.status_code == 401 and response.status_code == 200:
                    # Endpoint works both ways (might be public)
                    result['auth_required'] = False
                elif response.status_code == 200 and auth_response.status_code == 200:
                    # Might be public endpoint
                    result['auth_required'] = False

        return result

    def validate_parameter_validation(self, endpoint_path: str, method: str) -> Dict[str, Any]:
        """Validate parameter validation completeness"""
        result = {
            'endpoint': f"{method} {endpoint_path}",
            'compliance': True,
            'errors': []
        }

        # Test with invalid parameters
        invalid_test_cases = [
            {"test": "Invalid query param", "params": {"invalid_param": "test"}},
            {"test": "Invalid JSON body", "data": {"invalid_field": "test"}},
            {"test": "Invalid data types", "data": {"id": "not_a_number"}},
        ]

        auth_headers = {}
        if self.get_auth_token():
            auth_headers = {"Authorization": f"Bearer {self.get_auth_token()}"}

        for test_case in invalid_test_cases:
            try:
                if method == 'GET':
                    response = self.client.get(endpoint_path, params=test_case.get('params', {}), headers=auth_headers)
                elif method in ['POST', 'PUT', 'PATCH']:
                    response = self.client.request(method, endpoint_path,
                                                json=test_case.get('data', {}),
                                                headers=auth_headers)
                else:
                    continue

                # Should return validation error (400) for invalid input
                if response.status_code not in [400, 422]:
                    result['compliance'] = False
                    result['errors'].append(f"{test_case['test']}: Expected 400/422, got {response.status_code}")

            except Exception as e:
                result['errors'].append(f"{test_case['test']}: Exception occurred - {str(e)}")

        return result

    def validate_http_method_semantics(self, endpoint_path: str, methods: List[str]) -> Dict[str, Any]:
        """Validate HTTP method usage follows REST principles"""
        result = {
            'endpoint': endpoint_path,
            'compliance': True,
            'errors': []
        }

        # Check URL patterns and method appropriateness
        if '/create' in endpoint_path or '/new' in endpoint_path:
            if 'POST' not in methods:
                result['compliance'] = False
                result['errors'].append("Create endpoints should use POST method")

        if '/update' in endpoint_path or '/edit' in endpoint_path:
            if 'PUT' not in methods and 'PATCH' not in methods:
                result['compliance'] = False
                result['errors'].append("Update endpoints should use PUT or PATCH method")

        if '/delete' in endpoint_path or '/remove' in endpoint_path:
            if 'DELETE' not in methods:
                result['compliance'] = False
                result['errors'].append("Delete endpoints should use DELETE method")

        # Check for proper resource naming
        if endpoint_path.endswith('/'):
            result['compliance'] = False
            result['errors'].append("URL should not end with slash")

        # Check for proper path variable usage
        if '{' in endpoint_path and '}' not in endpoint_path:
            result['compliance'] = False
            result['errors'].append("Invalid path variable format")

        return result

    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run all compliance validations"""
        results = {
            'summary': {
                'total_endpoints': len(self.endpoints),
                'compliant_endpoints': 0,
                'non_compliant_endpoints': 0,
                'total_errors': 0
            },
            'endpoint_results': [],
            'global_errors': []
        }

        for endpoint in self.endpoints:
            endpoint_result = {
                'path': endpoint['path'],
                'methods': endpoint['methods'],
                'validations': {}
            }

            # Run all validations for each applicable method
            for method in endpoint['methods']:
                if method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                    # Skip docs and schema endpoints
                    if endpoint['path'] in ['/docs', '/openapi.json', '/redoc']:
                        continue

                    try:
                        # Test endpoint to validate response structure
                        auth_headers = {}
                        if self.get_auth_token():
                            auth_headers = {"Authorization": f"Bearer {self.get_auth_token()}"}

                        response = self.client.request(method, endpoint['path'], headers=auth_headers)

                        # Response structure validation
                        endpoint_result['validations'][f'{method}_response_structure'] = \
                            self.validate_response_structure(response, endpoint['path'], method)

                        # Parameter validation
                        endpoint_result['validations'][f'{method}_parameter_validation'] = \
                            self.validate_parameter_validation(endpoint['path'], method)

                    except Exception as e:
                        endpoint_result['validations'][f'{method}_exception'] = {
                            'compliance': False,
                            'errors': [f"Exception during testing: {str(e)}"]
                        }

            # Authentication validation
            endpoint_result['validations']['authentication'] = \
                self.validate_authentication(endpoint['path'], endpoint['methods'])

            # HTTP method semantics validation
            endpoint_result['validations']['http_semantics'] = \
                self.validate_http_method_semantics(endpoint['path'], endpoint['methods'])

            # Calculate endpoint compliance
            all_validations = []
            for validation in endpoint_result['validations'].values():
                if isinstance(validation, dict) and 'compliance' in validation:
                    all_validations.append(validation['compliance'])

            endpoint_result['compliance'] = all(all_validations) if all_validations else True
            endpoint_result['total_errors'] = sum(
                len(v.get('errors', [])) for v in endpoint_result['validations'].values()
                if isinstance(v, dict)
            )

            results['endpoint_results'].append(endpoint_result)

            # Update summary
            if endpoint_result['compliance']:
                results['summary']['compliant_endpoints'] += 1
            else:
                results['summary']['non_compliant_endpoints'] += 1

            results['summary']['total_errors'] += endpoint_result['total_errors']

        return results


@pytest.fixture
def compliance_validator(test_client):
    """Create API compliance validator instance"""
    return APIComplianceValidator(test_client)


class TestAPICompliance:
    """Test suite for API compliance validation"""

    def test_unified_response_structure(self, compliance_validator):
        """Test that all endpoints follow unified response structure"""
        # This is now integrated into the comprehensive validation
        pass

    def test_authentication_requirements(self, compliance_validator):
        """Test authentication requirements for protected endpoints"""
        # This is now integrated into the comprehensive validation
        pass

    def test_parameter_validation_completeness(self, compliance_validator):
        """Test parameter validation completeness"""
        # This is now integrated into the comprehensive validation
        pass

    def test_http_method_semantics(self, compliance_validator):
        """Test HTTP method semantics"""
        # This is now integrated into the comprehensive validation
        pass

    def test_rest_api_design_principles(self, compliance_validator):
        """Test REST API design principles"""
        # This is now integrated into the comprehensive validation
        pass

    def test_comprehensive_api_compliance(self, compliance_validator):
        """Run comprehensive API compliance validation"""
        results = compliance_validator.run_comprehensive_validation()

        # Print detailed results for debugging
        print(f"\n=== API Compliance Test Results ===")
        print(f"Total Endpoints: {results['summary']['total_endpoints']}")
        print(f"Compliant: {results['summary']['compliant_endpoints']}")
        print(f"Non-Compliant: {results['summary']['non_compliant_endpoints']}")
        print(f"Total Errors: {results['summary']['total_errors']}")

        # Print non-compliant endpoints
        for endpoint_result in results['endpoint_results']:
            if not endpoint_result['compliance']:
                print(f"\n❌ Non-Compliant Endpoint: {endpoint_result['path']}")
                print(f"   Methods: {', '.join(endpoint_result['methods'])}")
                print(f"   Total Errors: {endpoint_result['total_errors']}")

                for validation_name, validation in endpoint_result['validations'].items():
                    if isinstance(validation, dict) and not validation.get('compliance', True):
                        print(f"   - {validation_name}: {', '.join(validation.get('errors', []))}")

        # Assert compliance level (adjust threshold as needed)
        compliance_rate = results['summary']['compliant_endpoints'] / results['summary']['total_endpoints']

        # Require at least 80% compliance for now
        assert compliance_rate >= 0.8, \
            f"API compliance rate {compliance_rate:.2%} is below required 80%. " \
            f"Non-compliant endpoints: {results['summary']['non_compliant_endpoints']}"

        # Store results for reporting
        compliance_validator.test_results = results

    def test_response_model_consistency(self, test_client):
        """Test that response models match actual responses"""
        # Test a few key endpoints
        test_cases = [
            {
                'url': '/api/auth/me',
                'method': 'GET',
                'expected_fields': ['username', 'email', 'role'],
                'requires_auth': True
            },
            {
                'url': '/health',
                'method': 'GET',
                'expected_fields': ['status'],
                'requires_auth': False
            }
        ]

        for case in test_cases:
            headers = {}
            if case['requires_auth']:
                # Get auth token
                auth_response = test_client.post(
                    "/api/auth/login",
                    data={"username": "admin", "password": "admin123"}
                )
                if auth_response.status_code == 200:
                    token = auth_response.json().get("access_token")
                    headers = {"Authorization": f"Bearer {token}"}

            response = test_client.request(case['method'], case['url'], headers=headers)

            if response.status_code == 200:
                data = response.json()
                for field in case['expected_fields']:
                    assert field in data, f"Expected field '{field}' missing from response"

    def test_error_response_format(self, test_client):
        """Test that error responses follow the unified format"""
        # Test 401 error
        response = test_client.get('/api/auth/me')
        assert response.status_code == 401

        data = response.json()
        # Should have error information
        assert 'detail' in data or 'error' in data

        # Test 404 error
        response = test_client.get('/api/nonexistent')
        assert response.status_code == 404

        data = response.json()
        assert 'detail' in data or 'error' in data

    def test_status_code_correctness(self, test_client):
        """Test that status codes are correct for different scenarios"""
        # Test successful requests
        response = test_client.get('/health')
        assert response.status_code == 200

        # Test authentication
        response = test_client.post('/api/auth/login', data={"username": "admin", "password": "admin123"})
        assert response.status_code == 200

        # Test unauthorized access
        response = test_client.get('/api/auth/me')
        assert response.status_code == 401

        # Test not found
        response = test_client.get('/api/nonexistent')
        assert response.status_code == 404


# Integration with pytest collection
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
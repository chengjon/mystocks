def _check_all_endpoints(self) -> Dict:
    """检查所有端点"""
    results = {}

    for endpoint_name in self.registry.keys():
        results[endpoint_name] = self._check_single_endpoint(endpoint_name)

    total = len(results)
    healthy = sum(1 for r in results.values() if r["status"] == "healthy")
    unhealthy = total - healthy

    return {"total": total, "healthy": healthy, "unhealthy": unhealthy, "details": results}

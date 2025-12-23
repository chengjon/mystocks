"""Dummy FaultInjectionSystem for testing purposes."""


class FaultInjectionSystem:
    def inject_fault(self, fault_type: str) -> dict:
        return {"status": "fault_injected", "type": fault_type}

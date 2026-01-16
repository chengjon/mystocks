# MyStocks CI/CD Type Checking Integration

This directory contains scripts and configurations for integrating comprehensive type checking into the CI/CD pipeline.

## Overview

The type checking integration ensures code quality by running static type analysis before deployment:

- **Python Type Checking**: MyPy with strict configuration
- **TypeScript Type Checking**: Vue-TSC for Vue.js components
- **CI/CD Integration**: GitHub Actions workflow with type gates

## Files

### `.github/workflows/ci-cd-with-type-checking.yml`
GitHub Actions workflow that integrates type checking into the full CI/CD pipeline:

- **Type Check Job**: Runs mypy and vue-tsc in parallel
- **Code Quality Job**: Black, Ruff, Bandit, Safety, ESLint
- **Three-Layer Testing**: Unit → Integration → E2E
- **Performance Tests**: Lighthouse auditing
- **Deployment Jobs**: Test and production environments

### `scripts/cicd_pipeline.sh` (Updated)
Enhanced local CI/CD pipeline script with strict type checking:

- **Backend Type Check**: MyPy validation with config/mypy.ini
- **Frontend Type Check**: Vue-TSC compilation check
- **Code Quality Gates**: Black formatting, Ruff linting
- **Strict Failure Policy**: Type errors block deployment

## Type Checking Configurations

### Python (MyPy)
- **Config**: `config/mypy.ini`
- **Strict Settings**: `strict=True`, `noImplicitAny=True`
- **Exclusions**: Tests, scripts, third-party imports
- **Integration**: `--config-file=config/mypy.ini --package src`

### TypeScript (Vue-TSC)
- **Config**: `web/frontend/tsconfig.json`
- **Strict Mode**: Enabled for production code
- **Gradual Adoption**: Allows JS/TS coexistence
- **Integration**: `npx vue-tsc --noEmit`

## Usage

### GitHub Actions (Recommended)
```bash
# Automatic on push/PR to main/develop branches
# Type checking runs first, blocks if errors found
```

### Local Pipeline
```bash
# Run full pipeline with type checking
./scripts/cicd_pipeline.sh

# Type errors will cause immediate failure
```

### Individual Checks
```bash
# Python type check only
mypy --config-file=config/mypy.ini --package src

# TypeScript type check only
cd web/frontend && npx vue-tsc --noEmit
```

## Error Handling

### Type Check Failures
- **Python**: MyPy errors displayed with line numbers
- **TypeScript**: Vue-TSC compilation errors with suggestions
- **CI/CD**: Pipeline stops on first type error
- **Local**: Clear error messages with fix suggestions

### Common Issues

#### Python Type Issues
```bash
# Missing type hints
def function(param):  # ❌
def function(param: str) -> bool:  # ✅

# Any type usage
variable: Any  # ❌ - avoid Any when possible
variable: str | None  # ✅ - use union types
```

#### TypeScript Issues
```typescript
// Implicit any
const data = response.data;  // ❌
// Fix: Add type annotation
const data: UserData = response.data;  // ✅
```

## Integration Benefits

### Code Quality
- **Early Error Detection**: Catch type errors before runtime
- **IDE Support**: Better autocomplete and refactoring
- **Documentation**: Types serve as living documentation
- **Type Coverage Tracking**: Automated coverage reports and thresholds

### Development Workflow
- **CI/CD Gates**: Prevent type errors from reaching production
- **Team Consistency**: Enforced coding standards
- **Refactoring Safety**: Type system guides safe changes
- **Caching Optimization**: Faster CI/CD builds with MyPy/Vue-TSC caching

### Performance
- **Runtime Safety**: Reduce type-related runtime errors
- **Optimization**: Type information enables better optimization
- **Maintainability**: Self-documenting code reduces bugs
- **Quantitative Platform Specific**: Strategy performance validation

### Production Safety
- **Manual Approval Gates**: Production deployments require human approval
- **Automated Health Checks**: Post-deployment verification
- **Emergency Rollback**: Automatic rollback on health check failures
- **Comprehensive Monitoring**: Multi-layer deployment validation

## Advanced Features

### Performance Optimization
- **MyPy Caching**: `.mypy_cache` directory caching reduces build times
- **Vue-TSC Caching**: TypeScript compilation caching for faster frontend builds
- **Dependency Caching**: Python and Node.js package caching across builds

### Type Coverage Reporting
- **HTML Reports**: Visual type checking reports with error details
- **XML Reports**: Machine-readable format for CI/CD integration
- **Coverage Metrics**: Automated calculation of type coverage percentage
- **Threshold Enforcement**: Configurable minimum coverage requirements

### Production Deployment Safety
- **Manual Approval**: Production deployments require explicit approval
- **Health Checks**: Automated post-deployment verification
  - Backend API accessibility (`/docs` endpoint)
  - Frontend page loading
  - Core trading functionality (quantitative platform specific)
- **Emergency Rollback**: Automatic rollback on health check failures

### Quantitative Platform Enhancements
- **Strategy Performance Testing**: Specialized performance validation for trading strategies
- **Memory Usage Monitoring**: Track computational resource usage
- **Computation Time Thresholds**: Ensure strategy calculations meet performance requirements

## Migration Strategy

### Phase 1: Strict Type Checking (Current)
- Enable strict type checking for new code
- Allow gradual migration of existing code
- Type errors block CI/CD deployment

### Phase 2: Performance Optimization (Implemented)
- MyPy and Vue-TSC caching for faster builds
- Type coverage reporting and monitoring
- Production safety gates with rollback capabilities

### Phase 3: Full Coverage (Future)
- 95%+ type coverage target
- Complete migration of legacy code
- Advanced type features (generics, conditional types)

## Troubleshooting

### MyPy Issues
```bash
# Update stubs for third-party libraries
pip install types-requests types-pandas

# Ignore specific files
# Add to mypy.ini [mypy]
# exclude = file_to_ignore.py
```

### Vue-TSC Issues
```typescript
// For Vue components, ensure proper typing
<script setup lang="ts">
// Use defineProps with types
const props = defineProps<{
  data: UserData[]
  loading: boolean
}>()
</script>
```

### CI/CD Debugging
```bash
# Run locally to debug
./scripts/cicd_pipeline.sh

# Check specific type check
mypy --config-file=config/mypy.ini --package src --show-error-codes
```

## Related Documentation

- [CI/CD Optimization System](docs/guides/MYSTOCKS_CI_CD_OPTIMIZATION_SYSTEM.md)
- [MyPy Configuration Guide](config/mypy.ini)
- [TypeScript Config Guide](web/frontend/tsconfig.json)
- [Testing Architecture](docs/e2e-testing-ci-cd-architecture.md)
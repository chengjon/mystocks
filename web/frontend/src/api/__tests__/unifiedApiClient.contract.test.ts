import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ContractValidationError, contractValidator } from '../unifiedApiClient'

// Mock request function
vi.mock('../index.js', () => ({
    default: vi.fn()
}))

import request from '../index.js'

const mockRequest = vi.mocked(request)

describe('RuntimeContractValidator', () => {
    beforeEach(() => {
        // Clear cache and reset validation state
        contractValidator.clearCache()
        contractValidator.setValidationEnabled(true)

        // Reset mocks
        vi.clearAllMocks()
    })

    describe('validateResponse', () => {
        it('should pass validation for valid response', async () => {
            // Mock successful contract fetch
            mockRequest.mockResolvedValueOnce({
                success: true,
                data: {
                    spec: {
                        paths: {
                            '/api/test': {
                                get: {
                                    responses: {
                                        '200': {
                                            content: {
                                                'application/json': {
                                                    schema: {
                                                        type: 'object',
                                                        properties: {
                                                            success: { type: 'boolean' },
                                                            data: { type: 'string' }
                                                        },
                                                        required: ['success']
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            })

            const validResponse = {
                success: true,
                data: 'test data'
            }

            await expect(contractValidator.validateResponse('/api/test', 'GET', validResponse))
                .resolves.toBeUndefined()
        })

        it('should throw ContractValidationError for invalid response', async () => {
            // Mock successful contract fetch
            mockRequest.mockResolvedValueOnce({
                success: true,
                data: {
                    spec: {
                        paths: {
                            '/api/test': {
                                get: {
                                    responses: {
                                        '200': {
                                            content: {
                                                'application/json': {
                                                    schema: {
                                                        type: 'object',
                                                        properties: {
                                                            success: { type: 'boolean' },
                                                            data: { type: 'string' }
                                                        },
                                                        required: ['success']
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            })

            const invalidResponse = {
                data: 'missing success field'
            }

            await expect(contractValidator.validateResponse('/api/test', 'GET', invalidResponse))
                .rejects.toThrow(ContractValidationError)
        })

        it('should skip validation when disabled', async () => {
            contractValidator.setValidationEnabled(false)

            const response = { invalid: 'data' }

            await expect(contractValidator.validateResponse('/api/test', 'GET', response))
                .resolves.toBeUndefined()

            // Should not make any requests
            expect(mockRequest).not.toHaveBeenCalled()
        })

        it('should handle contract fetch failure gracefully', async () => {
            mockRequest.mockRejectedValueOnce(new Error('Network error'))

            const response = { success: true }

            // In development mode, should throw
            const originalEnv = import.meta.env.DEV
            import.meta.env.DEV = true

            await expect(contractValidator.validateResponse('/api/test', 'GET', response))
                .rejects.toThrow(ContractValidationError)

            import.meta.env.DEV = originalEnv
        })

        it('should cache contract schemas', async () => {
            mockRequest.mockResolvedValueOnce({
                success: true,
                data: {
                    spec: {
                        paths: {
                            '/api/test': {
                                get: {
                                    responses: {
                                        '200': {
                                            content: {
                                                'application/json': {
                                                    schema: { type: 'object', properties: { success: { type: 'boolean' } } }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            })

            // First call should fetch from API
            await contractValidator.validateResponse('/api/test', 'GET', { success: true })
            expect(mockRequest).toHaveBeenCalledTimes(1)

            // Second call should use cache
            await contractValidator.validateResponse('/api/test', 'GET', { success: true })
            expect(mockRequest).toHaveBeenCalledTimes(1) // Still 1 call
        })
    })

    describe('convertJsonSchemaToZod', () => {
        it('should convert string schema', () => {
            const validator = contractValidator as any
            const schema = validator.convertJsonSchemaToZod({ type: 'string' })

            expect(schema._def.typeName).toBe('ZodString')
        })

        it('should convert number schema with constraints', () => {
            const validator = contractValidator as any
            const schema = validator.convertJsonSchemaToZod({
                type: 'number',
                minimum: 0,
                maximum: 100
            })

            expect(schema._def.typeName).toBe('ZodNumber')
        })

        it('should convert boolean schema', () => {
            const validator = contractValidator as any
            const schema = validator.convertJsonSchemaToZod({ type: 'boolean' })

            expect(schema._def.typeName).toBe('ZodBoolean')
        })

        it('should convert array schema', () => {
            const validator = contractValidator as any
            const schema = validator.convertJsonSchemaToZod({
                type: 'array',
                items: { type: 'string' }
            })

            expect(schema._def.typeName).toBe('ZodArray')
        })

        it('should convert object schema', () => {
            const validator = contractValidator as any
            const schema = validator.convertJsonSchemaToZod({
                type: 'object',
                properties: {
                    name: { type: 'string' },
                    age: { type: 'number' }
                },
                required: ['name']
            })

            expect(schema._def.typeName).toBe('ZodObject')
        })
    })

    describe('getContractName', () => {
        it('should extract contract name from API path', () => {
            const validator = contractValidator as any

            expect(validator.getContractName('/api/market/symbols')).toBe('market-api')
            expect(validator.getContractName('/api/auth/login')).toBe('auth-api')
            expect(validator.getContractName('/api/user/profile')).toBe('user-api')
        })

        it('should return default name for unknown paths', () => {
            const validator = contractValidator as any

            expect(validator.getContractName('/unknown/path')).toBe('default-api')
            expect(validator.getContractName('/api')).toBe('default-api')
        })
    })
})
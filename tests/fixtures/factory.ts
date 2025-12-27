export const TestDataFactory = {
  createValidUser: (role = 'user') => ({
    id: `user_${Date.now()}`,
    username: `test_${role}`,
    permissions: role === 'admin' ? ['*'] : ['read']
  }),
  createMockStockData: (symbol = 'AAPL') => ({
    symbol,
    price: Math.random() * 1000,
    timestamp: new Date().toISOString()
  }),
  createStandardApiResponse: (data) => ({
    success: true,
    code: 200,
    data: data,
    message: "Success"
  })
};

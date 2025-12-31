/**
 * 测试数据配置
 *
 * 提供测试用户数据和常用测试场景数据
 */

export interface TestUser {
  username: string;
  password: string;
  role: 'admin' | 'user';
}

export const TEST_USERS: Record<string, TestUser> = {
  admin: {
    username: 'admin',
    password: 'admin123',
    role: 'admin',
  },
  user: {
    username: 'user',
    password: 'user123',
    role: 'user',
  },
  invalid: {
    username: 'invalid',
    password: 'wrongpassword',
    role: 'user',
  },
};

export const TEST_CREDENTIALS = {
  valid: {
    admin: TEST_USERS.admin,
    user: TEST_USERS.user,
  },
  invalid: {
    emptyUsername: { username: '', password: 'admin123' },
    emptyPassword: { username: 'admin', password: '' },
    wrongPassword: { username: 'admin', password: 'wrongpassword' },
    bothEmpty: { username: '', password: '' },
  },
};

export const TEST_URLS = {
  frontend: process.env.BASE_URL || 'http://localhost:3000',
  backend: process.env.API_BASE_URL || 'http://localhost:8000',
  login: `${process.env.BASE_URL || 'http://localhost:3000'}/login`,
};

export const TIMEOUTS = {
  default: 10000,
  navigation: 30000,
  login: 2000,
  short: 1000,
};

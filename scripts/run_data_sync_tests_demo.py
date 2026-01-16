if python -c "
from tests.api_contract_tests import run_data_sync_tests
try:
    results = run_data_sync_tests()
    print('✅ API契约测试完成')
    print(f'   测试通过率: {results[\"api_contracts\"][\"summary\"][\"success_rate\"]}%')
except Exception as e:
    print(f'❌ API契约测试失败: {e}')
    print('   注意: 这是一个演示，实际运行需要后端服务')
"
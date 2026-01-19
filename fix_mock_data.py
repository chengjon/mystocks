import os

def fix_strategy_mock():
    file_path = 'web/frontend/src/mock/strategyMock.ts'
    with open(file_path, 'r') as f:
        content = f.read()

    # Fix BacktestTask: add 'id' field where missing
    # The error "Property 'id' is missing in type ... but required in type 'BacktestTask'" suggests 'id' is required.
    # In my previous step, I made 'id' optional in BacktestTask interface: "id?: string;".
    # But maybe the type check hasn't picked it up yet or I need to be more explicit.
    # Regardless, it is better practice for Mock data to have the canonical ID field.
    
    # In mockBacktestTask:
    if "task_id: 'bt_20250125_001'," in content and "id: 'bt_20250125_001'," not in content:
        content = content.replace("task_id: 'bt_20250125_001',", "id: 'bt_20250125_001',\n  task_id: 'bt_20250125_001',")
        
    # In mockBacktestTasks list items:
    if "task_id: 'bt_20250124_003'," in content and "id: 'bt_20250124_003'," not in content:
        content = content.replace("task_id: 'bt_20250124_003',", "id: 'bt_20250124_003',\n    task_id: 'bt_20250124_003',")
        
    if "task_id: 'bt_20250125_002'," in content and "id: 'bt_20250125_002'," not in content:
        content = content.replace("task_id: 'bt_20250125_002',", "id: 'bt_20250125_002',\n    task_id: 'bt_20250125_002',")

    # Fix BacktestResultVM: add 'strategy_id' and 'total_return' where missing or aliased
    # The mock uses 'total_return' (snake) but maybe interface expects it or adapter uses it.
    # Error: "Object literal may only specify known properties, and 'total_return' does not exist in type 'BacktestResultVM'."
    # Wait, BacktestResultVM has [key: string]: any; now. So unknown properties should be allowed.
    # But previous error logs were before I added index signature?
    # "type_check_round_5.txt" was generated BEFORE I ran "fix_ts_errors_round3.py".
    # So the index signature fix should theoretically solve the "does not exist" errors.
    
    # However, to be safe and "unified", let's ensure snake_case fields are present if expected by new types.
    
    # StrategyPerformance in Mock:
    # It has: totalReturn, annualReturn (not annualizedReturn), sharpeRatio...
    # Interface expects: total_return, sharpe_ratio... AND camelCase aliases.
    # I updated Interface to have optional camelCase aliases.
    # But the Mock is missing the snake_case ones which might be required if I didn't make them optional.
    # I made them optional in round 3.
    
    # So, essentially, my previous Type fixes (Round 3) SHOULD have fixed most Mock errors
    # IF the Mock data was just missing optional fields or using aliases.
    
    # But let's proactively add the 'id' field to BacktestTasks in the mock, 
    # because 'id' is usually the standard.
    
    with open(file_path, 'w') as f:
        f.write(content)
    print(f"Refined {file_path}")

if __name__ == '__main__':
    fix_strategy_mock()

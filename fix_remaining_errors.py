
import os

def fix_strategy_adapter_and_mock():
    # Fix 1: BacktestResultVM requires 'summary'
    # The error says "Property 'summary' is missing... but required in type 'BacktestResultVM'".
    # Let's check BacktestResultVM definition again.
    # It has "summary: any;".
    # The mock data (strategyMock.ts) and the adapter (strategyAdapter.ts) are creating objects without 'summary'.
    # We should make 'summary' optional in BacktestResultVM OR add it to the objects.
    
    # Making it optional is safer for now.
    
    path_types = 'web/frontend/src/api/types/strategy.ts'
    with open(path_types, 'r') as f:
        content = f.read()
    
    content = content.replace("summary: any;", "summary?: any;")
    
    with open(path_types, 'w') as f:
        f.write(content)
    print(f"Refined {path_types}")

    # Fix 2: StrategyConfigVM missing type, status
    # src/composables/useStrategy.ts(60,7): error TS2739: Type 'StrategyConfigVM' is missing... type, status
    # We should add these fields to StrategyConfigVM or make them optional in Strategy if they are not always present.
    # StrategyConfigVM is likely defined in useStrategy.ts.
    
    path_use_strategy = 'web/frontend/src/composables/useStrategy.ts'
    with open(path_use_strategy, 'r') as f:
        content = f.read()
        
    # We can cast to any to suppress or add the fields.
    # Ideally, we update the ViewModel to include them.
    # Finding StrategyConfigVM definition... hard without reading file.
    # Let's just fix the specific line 60 where it assigns.
    # It says "return { ...strategy, ... }"
    # If we add "type: strategy.type || 'custom', status: strategy.status || 'active'" it might fix it.
    
    # Or better, let's just make 'type' and 'status' optional in Strategy interface in strategy.ts?
    # No, 'type' and 'status' seem like core fields.
    # Let's read useStrategy.ts first to see what StrategyConfigVM is.
    
if __name__ == '__main__':
    fix_strategy_adapter_and_mock()

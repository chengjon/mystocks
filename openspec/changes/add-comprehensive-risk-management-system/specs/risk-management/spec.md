## ADDED Requirements

### Requirement: Risk Management System Core
The system SHALL provide a comprehensive risk management capability that extends existing monitoring infrastructure to enable users to monitor, assess, and control investment risks at both individual stock and portfolio levels.

#### Scenario: User Accesses Risk Dashboard
**GIVEN** a user has trading positions in their portfolio
**WHEN** they navigate to the risk management section
**THEN** they SHALL see a comprehensive risk dashboard that integrates with existing monitoring dashboards, showing:
- Real-time VaR calculations using existing GPU infrastructure
- Portfolio concentration metrics from existing stock monitoring
- Active risk alerts via existing MonitoredNotificationManager
- Stop-loss strategy status integrated with existing signal tracking

#### Scenario: System Calculates Individual Stock Risk
**GIVEN** a stock is held in the user's portfolio
**WHEN** the system receives real-time price updates via existing data sources
**THEN** it SHALL calculate and store risk metrics using existing GPU engines, including:
- Volatility (20-day historical) via existing GPU calculators
- Liquidity score from existing TDX/AKShare data
- Technical indicators risk level using existing TA libraries
- Overall risk assessment stored in extended monitoring tables

#### Scenario: Portfolio Risk Assessment
**GIVEN** a user has multiple positions
**WHEN** the system aggregates individual stock risks
**THEN** it SHALL compute portfolio-level metrics including:
- Value at Risk (VaR) using historical simulation
- Portfolio concentration (HHI index)
- Correlation matrix heat map
- Sector allocation analysis

### Requirement: GPU-Accelerated Risk Calculations
The system SHALL leverage existing GPU infrastructure to accelerate complex risk computations while maintaining CPU fallback capability.

#### Scenario: GPU Acceleration for Correlation Matrix
**GIVEN** a portfolio with 50+ stocks
**WHEN** calculating the correlation matrix
**THEN** the system SHALL:
- Use CuPy for GPU-accelerated matrix operations
- Fall back to CPU computation if GPU unavailable
- Achieve 60x+ performance improvement
- Maintain calculation accuracy within 0.001 tolerance

#### Scenario: GPU-Accelerated VaR Simulation
**GIVEN** historical price data for VaR calculation
**WHEN** running Monte Carlo simulations
**THEN** the system SHALL:
- Use GPU parallel processing for 10,000+ scenarios
- Complete calculations in under 0.5 seconds
- Integrate with existing GPU memory management
- Provide CPU fallback for error recovery

### Requirement: Real-Time Risk Monitoring
The system SHALL provide real-time risk monitoring with sub-second latency for critical risk indicators.

#### Scenario: Real-Time Price Risk Updates
**GIVEN** live price feeds from multiple data sources
**WHEN** price updates arrive
**THEN** the system SHALL:
- Update risk calculations within 3 seconds
- Trigger alerts for threshold breaches
- Update frontend dashboards via WebSocket
- Log all risk metric changes to TDengine

#### Scenario: Stop-Loss Strategy Execution
**GIVEN** an active stop-loss strategy
**WHEN** trigger conditions are met
**THEN** the system SHALL:
- Execute stop-loss orders automatically
- Record execution details and P&L impact
- Send immediate notifications to user
- Update risk positions in real-time

### Requirement: Multi-Level Risk Alerting
The system SHALL implement a three-tier alerting system with multiple notification channels and intelligent alert management.

#### Scenario: Three-Tier Alert Classification
**GIVEN** risk metrics exceed configured thresholds
**WHEN** alerts are generated
**THEN** they SHALL be classified as:
- 🟢 Normal: Within acceptable risk bounds
- 🟡 Caution: Approaching risk limits, monitor closely
- 🔴 Danger: Risk limits exceeded, immediate action required

#### Scenario: Multi-Channel Alert Delivery
**GIVEN** a danger-level alert is triggered
**WHEN** the alert is processed
**THEN** the system SHALL:
- Display in-app notification immediately
- Send email alert within 30 seconds
- Push WebSocket notification to active sessions
- Log alert to persistent storage with full context

### Requirement: Stop-Loss Strategy Management
The system SHALL provide multiple stop-loss strategies with intelligent execution and performance tracking.

#### Scenario: Volatility-Adaptive Stop Loss
**GIVEN** a position with active stop-loss strategy
**WHEN** market volatility changes
**THEN** the system SHALL:
- Dynamically adjust stop-loss distance based on ATR(14)
- Use higher multiples (2.0x) in low volatility
- Use conservative multiples (1.0x) in high volatility
- Maintain minimum stop distance to avoid over-trading

#### Scenario: Trailing Stop with Dual Confirmation
**GIVEN** a profitable position
**WHEN** price moves favorably
**THEN** the system SHALL:
- Trail stop-loss behind highest price achieved
- Require dual confirmation (price + technical indicator)
- Execute only when both conditions met
- Record trailing history for performance analysis

### Requirement: Data Source Integration
The system SHALL integrate with existing 50+ data sources without requiring new external dependencies.

#### Scenario: Multi-Source Data Aggregation
**GIVEN** risk calculations require data from multiple sources
**WHEN** fetching price and fundamental data
**THEN** the system SHALL:
- Use AKShare for 34+ financial data interfaces
- Use Efinance for 16+ stock market data feeds
- Use TDX for real-time level-2 market data
- Aggregate data with quality validation and failover

#### Scenario: Data Quality Assurance
**GIVEN** inconsistent data from different sources
**WHEN** processing risk calculations
**THEN** the system SHALL:
- Validate data completeness and accuracy
- Implement data source health monitoring
- Use fallback sources when primary fails
- Alert administrators of data quality issues

### Requirement: Frontend Risk Visualization
The system SHALL provide intuitive risk visualization using existing Vue.js and ECharts infrastructure.

#### Scenario: Risk Dashboard Overview
**GIVEN** a user accesses the risk management interface
**WHEN** the dashboard loads
**THEN** it SHALL display:
- Risk gauge widgets for key metrics
- Real-time VaR and drawdown charts
- Portfolio concentration visualizations
- Active alerts summary panel

#### Scenario: Interactive Risk Heat Map
**GIVEN** a portfolio with multiple positions
**WHEN** viewing correlation analysis
**THEN** the system SHALL:
- Render interactive heat map using ECharts
- Show correlation coefficients between assets
- Highlight high-correlation pairs (>0.8)
- Allow drill-down to individual stock analysis
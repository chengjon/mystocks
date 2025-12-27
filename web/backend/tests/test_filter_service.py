"""
高级订阅过滤服务测试

Tests for Advanced Subscription & Filtering System

Task 8: 实现灵活的用户订阅过滤系统

Author: Claude Code
Date: 2025-11-07
"""

from datetime import datetime

from app.services.filter_service import (
    FilterCondition,
    FilterExpression,
    FilterOperator,
    FilterEvaluator,
    AlertPriority,
    AlertDeliveryMethod,
    AlertDispatcher,
    SubscriptionManager,
    Subscription,
    Alert,
    get_filter_evaluator,
    get_alert_dispatcher,
    get_subscription_manager,
    reset_filter_service,
)


class TestFilterCondition:
    """测试过滤条件"""

    def test_condition_creation(self):
        """测试条件创建"""
        condition = FilterCondition(field="price", operator=FilterOperator.GT, value=100.0)
        assert condition.field == "price"
        assert condition.operator == FilterOperator.GT
        assert condition.value == 100.0

    def test_numeric_comparison_gt(self):
        """测试数值大于比较"""
        condition = FilterCondition(field="price", operator=FilterOperator.GT, value=100.0)
        assert condition.matches({"price": 150.0}) is True
        assert condition.matches({"price": 100.0}) is False
        assert condition.matches({"price": 50.0}) is False

    def test_numeric_comparison_gte(self):
        """测试数值大于等于比较"""
        condition = FilterCondition(field="price", operator=FilterOperator.GTE, value=100.0)
        assert condition.matches({"price": 150.0}) is True
        assert condition.matches({"price": 100.0}) is True
        assert condition.matches({"price": 50.0}) is False

    def test_numeric_comparison_lt(self):
        """测试数值小于比较"""
        condition = FilterCondition(field="volume", operator=FilterOperator.LT, value=1000000)
        assert condition.matches({"volume": 500000}) is True
        assert condition.matches({"volume": 1000000}) is False
        assert condition.matches({"volume": 2000000}) is False

    def test_numeric_comparison_eq(self):
        """测试数值等于比较"""
        condition = FilterCondition(field="price", operator=FilterOperator.EQ, value=100.0)
        assert condition.matches({"price": 100.0}) is True
        assert condition.matches({"price": 100.1}) is False

    def test_numeric_comparison_ne(self):
        """测试数值不等于比较"""
        condition = FilterCondition(field="price", operator=FilterOperator.NE, value=100.0)
        assert condition.matches({"price": 100.1}) is True
        assert condition.matches({"price": 100.0}) is False

    def test_symbol_exact_match(self):
        """测试符号精确匹配"""
        condition = FilterCondition(field="symbol", operator=FilterOperator.EQ, value="600519")
        assert condition.matches({"symbol": "600519"}) is True
        assert condition.matches({"symbol": "000001"}) is False

    def test_symbol_wildcard_match(self):
        """测试符号通配符匹配"""
        condition = FilterCondition(field="symbol", operator=FilterOperator.MATCH, value="60*")
        assert condition.matches({"symbol": "600519"}) is True
        assert condition.matches({"symbol": "600000"}) is True
        assert condition.matches({"symbol": "000001"}) is False

    def test_symbol_regex_match(self):
        """测试符号正则匹配"""
        condition = FilterCondition(field="symbol", operator=FilterOperator.MATCH, value="6[0-9]{4}")
        assert condition.matches({"symbol": "600519"}) is True
        assert condition.matches({"symbol": "000001"}) is False

    def test_string_match(self):
        """测试字符串匹配"""
        condition = FilterCondition(
            field="name",
            operator=FilterOperator.MATCH,
            value="technology",
            case_sensitive=False,
        )
        assert condition.matches({"name": "Technology Company"}) is True
        assert condition.matches({"name": "Banking Company"}) is False

    def test_missing_field(self):
        """测试缺少字段"""
        condition = FilterCondition(field="price", operator=FilterOperator.GT, value=100.0)
        assert condition.matches({"volume": 1000}) is False

    def test_list_membership(self):
        """测试列表成员检查"""
        condition = FilterCondition(
            field="symbol",
            operator=FilterOperator.IN,
            value=["600519", "000001", "600000"],
        )
        assert condition.matches({"symbol": "600519"}) is True
        assert condition.matches({"symbol": "000001"}) is True
        assert condition.matches({"symbol": "999999"}) is False


class TestFilterExpression:
    """测试过滤表达式"""

    def test_expression_creation(self):
        """测试表达式创建"""
        expr = FilterExpression(id="expr_1", name="Price Filter", expression="price > 100")
        assert expr.id == "expr_1"
        assert expr.name == "Price Filter"
        assert expr.enabled is True

    def test_add_condition(self):
        """测试添加条件"""
        expr = FilterExpression(id="expr_1", name="Combined Filter", expression="")
        cond1 = FilterCondition(field="price", operator=FilterOperator.GT, value=100.0)
        cond2 = FilterCondition(field="volume", operator=FilterOperator.LT, value=1000000)

        expr.add_condition(cond1)
        expr.add_condition(cond2)

        assert len(expr.conditions) == 2

    def test_evaluate_and_logic(self):
        """测试AND逻辑"""
        expr = FilterExpression(id="expr_1", name="Combined Filter", expression="", logic="AND")

        expr.add_condition(FilterCondition(field="price", operator=FilterOperator.GT, value=100.0))
        expr.add_condition(FilterCondition(field="volume", operator=FilterOperator.LT, value=1000000))

        # 两个条件都满足
        assert expr.evaluate({"price": 150.0, "volume": 500000}) is True
        # 只有一个条件满足
        assert expr.evaluate({"price": 150.0, "volume": 2000000}) is False
        # 都不满足
        assert expr.evaluate({"price": 50.0, "volume": 2000000}) is False

    def test_evaluate_or_logic(self):
        """测试OR逻辑"""
        expr = FilterExpression(id="expr_1", name="Combined Filter", expression="", logic="OR")

        expr.add_condition(FilterCondition(field="price", operator=FilterOperator.GT, value=100.0))
        expr.add_condition(FilterCondition(field="volume", operator=FilterOperator.LT, value=1000000))

        # 两个条件都满足
        assert expr.evaluate({"price": 150.0, "volume": 500000}) is True
        # 只有一个条件满足
        assert expr.evaluate({"price": 150.0, "volume": 2000000}) is True
        # 都不满足
        assert expr.evaluate({"price": 50.0, "volume": 2000000}) is False

    def test_disabled_expression(self):
        """测试禁用表达式"""
        expr = FilterExpression(id="expr_1", name="Disabled Filter", expression="", enabled=False)
        expr.add_condition(FilterCondition(field="price", operator=FilterOperator.GT, value=100.0))

        # 禁用的表达式不应评估
        assert expr.evaluate({"price": 150.0}) is False

    def test_empty_conditions(self):
        """测试空条件"""
        expr = FilterExpression(id="expr_1", name="Empty Filter", expression="")
        assert expr.evaluate({"price": 150.0}) is False


class TestFilterEvaluator:
    """测试过滤评估器"""

    def test_evaluator_initialization(self):
        """测试评估器初始化"""
        evaluator = FilterEvaluator()
        assert len(evaluator.subscriptions) == 0
        assert evaluator.evaluations == 0
        assert evaluator.matches == 0

    def test_add_subscription(self):
        """测试添加订阅"""
        evaluator = FilterEvaluator()
        expr = FilterExpression(id="expr_1", name="Price Filter", expression="")
        sub = Subscription(
            id="sub_1",
            user_id="user_1",
            name="My Filter",
            filter_expr=expr,
        )

        evaluator.add_subscription(sub)
        assert len(evaluator.subscriptions) == 1
        assert "sub_1" in evaluator.subscriptions

    def test_remove_subscription(self):
        """测试移除订阅"""
        evaluator = FilterEvaluator()
        expr = FilterExpression(id="expr_1", name="Price Filter", expression="")
        sub = Subscription(
            id="sub_1",
            user_id="user_1",
            name="My Filter",
            filter_expr=expr,
        )

        evaluator.add_subscription(sub)
        assert evaluator.remove_subscription("sub_1") is True
        assert len(evaluator.subscriptions) == 0

    def test_evaluate_data_single_match(self):
        """测试单个匹配的数据评估"""
        evaluator = FilterEvaluator()

        expr = FilterExpression(id="expr_1", name="Price Filter", expression="")
        expr.add_condition(FilterCondition(field="price", operator=FilterOperator.GT, value=100.0))

        sub = Subscription(
            id="sub_1",
            user_id="user_1",
            name="My Filter",
            filter_expr=expr,
        )

        evaluator.add_subscription(sub)
        matched = evaluator.evaluate_data({"price": 150.0})

        assert len(matched) == 1
        assert "sub_1" in matched

    def test_evaluate_data_multiple_matches(self):
        """测试多个匹配的数据评估"""
        evaluator = FilterEvaluator()

        # 订阅1
        expr1 = FilterExpression(id="expr_1", name="Price Filter", expression="")
        expr1.add_condition(FilterCondition(field="price", operator=FilterOperator.GT, value=100.0))
        sub1 = Subscription(
            id="sub_1",
            user_id="user_1",
            name="Price Filter",
            filter_expr=expr1,
        )

        # 订阅2
        expr2 = FilterExpression(id="expr_2", name="Volume Filter", expression="")
        expr2.add_condition(FilterCondition(field="volume", operator=FilterOperator.LT, value=1000000))
        sub2 = Subscription(
            id="sub_2",
            user_id="user_1",
            name="Volume Filter",
            filter_expr=expr2,
        )

        evaluator.add_subscription(sub1)
        evaluator.add_subscription(sub2)

        matched = evaluator.evaluate_data({"price": 150.0, "volume": 500000})

        assert len(matched) == 2
        assert "sub_1" in matched
        assert "sub_2" in matched

    def test_evaluate_data_no_matches(self):
        """测试无匹配的数据评估"""
        evaluator = FilterEvaluator()

        expr = FilterExpression(id="expr_1", name="Price Filter", expression="")
        expr.add_condition(FilterCondition(field="price", operator=FilterOperator.GT, value=100.0))

        sub = Subscription(
            id="sub_1",
            user_id="user_1",
            name="My Filter",
            filter_expr=expr,
        )

        evaluator.add_subscription(sub)
        matched = evaluator.evaluate_data({"price": 50.0})

        assert len(matched) == 0

    def test_get_stats(self):
        """测试获取统计"""
        evaluator = FilterEvaluator()
        expr = FilterExpression(id="expr_1", name="Price Filter", expression="")
        sub = Subscription(
            id="sub_1",
            user_id="user_1",
            name="My Filter",
            filter_expr=expr,
        )

        evaluator.add_subscription(sub)
        evaluator.evaluate_data({"price": 150.0})

        stats = evaluator.get_stats()
        assert stats["total_subscriptions"] == 1
        assert stats["evaluations"] == 1


class TestAlertDispatcher:
    """测试告警分发器"""

    def test_dispatcher_initialization(self):
        """测试分发器初始化"""
        dispatcher = AlertDispatcher()
        assert len(dispatcher.alerts) == 0
        assert dispatcher.alerts_created == 0

    def test_register_delivery_handler(self):
        """测试注册交付处理器"""
        dispatcher = AlertDispatcher()

        def mock_handler(alert):
            return True

        dispatcher.register_delivery_handler(AlertDeliveryMethod.WEBSOCKET, mock_handler)
        assert AlertDeliveryMethod.WEBSOCKET in dispatcher.delivery_handlers

    def test_create_alert(self):
        """测试创建告警"""
        dispatcher = AlertDispatcher()

        alert = dispatcher.create_alert(
            subscription_id="sub_1",
            data={"price": 150.0, "symbol": "600519"},
            priority=AlertPriority.HIGH,
            delivery_methods={AlertDeliveryMethod.WEBSOCKET},
        )

        assert alert.subscription_id == "sub_1"
        assert alert.priority == AlertPriority.HIGH
        assert AlertDeliveryMethod.WEBSOCKET in alert.delivery_methods
        assert dispatcher.alerts_created == 1

    def test_dispatch_alert_success(self):
        """测试告警分发成功"""
        dispatcher = AlertDispatcher()

        def mock_handler(alert):
            return True

        dispatcher.register_delivery_handler(AlertDeliveryMethod.WEBSOCKET, mock_handler)

        alert = dispatcher.create_alert(
            subscription_id="sub_1",
            data={"price": 150.0},
            priority=AlertPriority.HIGH,
            delivery_methods={AlertDeliveryMethod.WEBSOCKET},
        )

        result = dispatcher.dispatch_alert(alert)
        assert result is True
        assert alert.delivered is True
        assert dispatcher.alerts_delivered == 1

    def test_dispatch_alert_failure(self):
        """测试告警分发失败"""
        dispatcher = AlertDispatcher()

        def mock_handler(alert):
            return False

        dispatcher.register_delivery_handler(AlertDeliveryMethod.WEBSOCKET, mock_handler)

        alert = dispatcher.create_alert(
            subscription_id="sub_1",
            data={"price": 150.0},
            priority=AlertPriority.HIGH,
            delivery_methods={AlertDeliveryMethod.WEBSOCKET},
        )

        result = dispatcher.dispatch_alert(alert)
        assert result is False
        assert alert.delivered is False

    def test_alert_to_dict(self):
        """测试告警转换为字典"""
        alert = Alert(
            id="alert_1",
            subscription_id="sub_1",
            timestamp=datetime.utcnow(),
            data={"price": 150.0},
            priority=AlertPriority.HIGH,
            delivery_methods={AlertDeliveryMethod.WEBSOCKET},
        )

        alert_dict = alert.to_dict()
        assert alert_dict["id"] == "alert_1"
        assert alert_dict["subscription_id"] == "sub_1"
        assert alert_dict["priority"] == "high"


class TestSubscriptionManager:
    """测试订阅管理器"""

    def setup_method(self):
        """每个测试前重置"""
        reset_filter_service()

    def test_manager_initialization(self):
        """测试管理器初始化"""
        manager = SubscriptionManager()
        assert len(manager.subscriptions) == 0
        assert manager.evaluator is not None
        assert manager.dispatcher is not None

    def test_create_subscription(self):
        """测试创建订阅"""
        manager = SubscriptionManager()

        expr = FilterExpression(id="expr_1", name="Price Filter", expression="")
        expr.add_condition(FilterCondition(field="price", operator=FilterOperator.GT, value=100.0))

        sub = manager.create_subscription(
            user_id="user_1",
            name="My Subscription",
            filter_expr=expr,
            priority=AlertPriority.HIGH,
        )

        assert sub.user_id == "user_1"
        assert sub.name == "My Subscription"
        assert len(manager.subscriptions) == 1

    def test_delete_subscription(self):
        """测试删除订阅"""
        manager = SubscriptionManager()

        expr = FilterExpression(id="expr_1", name="Price Filter", expression="")
        sub = manager.create_subscription(
            user_id="user_1",
            name="My Subscription",
            filter_expr=expr,
        )

        assert manager.delete_subscription(sub.id) is True
        assert len(manager.subscriptions) == 0

    def test_get_user_subscriptions(self):
        """测试获取用户订阅"""
        manager = SubscriptionManager()

        expr = FilterExpression(id="expr_1", name="Price Filter", expression="")

        sub1 = manager.create_subscription(
            user_id="user_1",
            name="Sub1",
            filter_expr=expr,
        )

        sub2 = manager.create_subscription(
            user_id="user_1",
            name="Sub2",
            filter_expr=expr,
        )

        subs = manager.get_user_subscriptions("user_1")
        assert len(subs) == 2

    def test_enable_disable_subscription(self):
        """测试启用禁用订阅"""
        manager = SubscriptionManager()

        expr = FilterExpression(id="expr_1", name="Price Filter", expression="")
        sub = manager.create_subscription(
            user_id="user_1",
            name="My Subscription",
            filter_expr=expr,
        )

        assert manager.disable_subscription(sub.id) is True
        assert manager.subscriptions[sub.id].enabled is False

        assert manager.enable_subscription(sub.id) is True
        assert manager.subscriptions[sub.id].enabled is True

    def test_process_data(self):
        """测试处理数据"""
        manager = SubscriptionManager()

        expr = FilterExpression(id="expr_1", name="Price Filter", expression="")
        expr.add_condition(FilterCondition(field="price", operator=FilterOperator.GT, value=100.0))

        sub = manager.create_subscription(
            user_id="user_1",
            name="My Subscription",
            filter_expr=expr,
        )

        # 注册mock处理器
        def mock_handler(alert):
            return True

        manager.dispatcher.register_delivery_handler(AlertDeliveryMethod.WEBSOCKET, mock_handler)

        # 处理匹配的数据
        matched = manager.process_data({"price": 150.0})
        assert len(matched) == 1
        assert sub.id in matched

    def test_get_stats(self):
        """测试获取统计"""
        manager = SubscriptionManager()

        expr = FilterExpression(id="expr_1", name="Price Filter", expression="")
        manager.create_subscription(
            user_id="user_1",
            name="My Subscription",
            filter_expr=expr,
        )

        stats = manager.get_stats()
        assert stats["total_subscriptions"] == 1
        assert stats["total_users"] == 1


class TestFilterServiceSingletons:
    """测试过滤服务单例"""

    def setup_method(self):
        """每个测试前重置"""
        reset_filter_service()

    def test_get_filter_evaluator(self):
        """测试获取过滤评估器单例"""
        evaluator1 = get_filter_evaluator()
        evaluator2 = get_filter_evaluator()
        assert evaluator1 is evaluator2

    def test_get_alert_dispatcher(self):
        """测试获取告警分发器单例"""
        dispatcher1 = get_alert_dispatcher()
        dispatcher2 = get_alert_dispatcher()
        assert dispatcher1 is dispatcher2

    def test_get_subscription_manager(self):
        """测试获取订阅管理器单例"""
        manager1 = get_subscription_manager()
        manager2 = get_subscription_manager()
        assert manager1 is manager2

    def test_reset_filter_service(self):
        """测试重置过滤服务"""
        manager1 = get_subscription_manager()
        reset_filter_service()
        manager2 = get_subscription_manager()
        assert manager1 is not manager2


class TestComplexScenarios:
    """测试复杂场景"""

    def setup_method(self):
        """每个测试前重置"""
        reset_filter_service()

    def test_multiple_conditions_and_subscriptions(self):
        """测试多个条件和订阅"""
        manager = SubscriptionManager()

        # 订阅1：价格>100且成交量<1M
        expr1 = FilterExpression(id="expr_1", name="Combined", expression="", logic="AND")
        expr1.add_condition(FilterCondition(field="price", operator=FilterOperator.GT, value=100.0))
        expr1.add_condition(FilterCondition(field="volume", operator=FilterOperator.LT, value=1000000))

        sub1 = manager.create_subscription(user_id="user_1", name="Sub1", filter_expr=expr1)

        # 订阅2：价格<50或成交量>2M
        expr2 = FilterExpression(id="expr_2", name="Combined", expression="", logic="OR")
        expr2.add_condition(FilterCondition(field="price", operator=FilterOperator.LT, value=50.0))
        expr2.add_condition(FilterCondition(field="volume", operator=FilterOperator.GT, value=2000000))

        sub2 = manager.create_subscription(user_id="user_2", name="Sub2", filter_expr=expr2)

        # 注册handler
        def mock_handler(alert):
            return True

        manager.dispatcher.register_delivery_handler(AlertDeliveryMethod.WEBSOCKET, mock_handler)

        # 测试数据1：符合Sub1
        matched1 = manager.process_data({"price": 150.0, "volume": 500000})
        assert sub1.id in matched1
        assert sub2.id not in matched1

        # 测试数据2：符合Sub2
        matched2 = manager.process_data({"price": 30.0, "volume": 500000})
        assert sub1.id not in matched2
        assert sub2.id in matched2

        # 测试数据3：都符合
        matched3 = manager.process_data({"price": 150.0, "volume": 2500000})
        assert sub1.id not in matched3  # 成交量太大
        assert sub2.id in matched3

    def test_symbol_filtering(self):
        """测试符号过滤"""
        manager = SubscriptionManager()

        # 订阅：符号以6开头
        expr = FilterExpression(id="expr_1", name="Symbol Filter", expression="")
        expr.add_condition(FilterCondition(field="symbol", operator=FilterOperator.MATCH, value="6.*"))

        sub = manager.create_subscription(user_id="user_1", name="Sub", filter_expr=expr)

        def mock_handler(alert):
            return True

        manager.dispatcher.register_delivery_handler(AlertDeliveryMethod.WEBSOCKET, mock_handler)

        matched1 = manager.process_data({"symbol": "600519"})
        assert sub.id in matched1

        matched2 = manager.process_data({"symbol": "000001"})
        assert sub.id not in matched2

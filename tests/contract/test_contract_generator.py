"""
API契约生成器测试

提供从现有代码生成OpenAPI规范的功能，支持反向工程API契约。
"""

import inspect
import json
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from fastapi import FastAPI
from pydantic import BaseModel
from pydantic.fields import FieldInfo


class ContractSourceType(Enum):
    """契约源类型枚举"""

    FASTAPI = "fastapi"
    FASTAPI_FILE = "fastapi_file"
    ROUTE_FUNCTION = "route_function"
    YAML_FILE = "yaml_file"
    JSON_FILE = "json_file"
    AUTO_DETECT = "auto_detect"


class ValidationLevel(Enum):
    """验证级别枚举"""

    STRICT = "strict"
    MODERATE = "moderate"
    LENIENT = "lenient"


class MediaType(Enum):
    """媒体类型枚举"""

    JSON = "application/json"
    FORM_URL_ENCODED = "application/x-www-form-urlencoded"
    MULTIPART_FORM_DATA = "multipart/form-data"
    TEXT_PLAIN = "text/plain"
    HTML = "text/html"
    XML = "application/xml"


@dataclass
class Parameter:
    """参数定义"""

    name: str
    type: str
    required: bool = True
    description: str = ""
    default: Any = None
    example: Any = None
    enum: List[Any] = field(default_factory=list)
    validation_rules: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Response:
    """响应定义"""

    status_code: int
    description: str
    content_type: str = MediaType.JSON.value
    schema: Dict[str, Any] = field(default_factory=dict)
    examples: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class PathItem:
    """路径项定义"""

    path: str
    method: str
    summary: str = ""
    description: str = ""
    parameters: List[Parameter] = field(default_factory=list)
    request_body: Dict[str, Any] = field(default_factory=dict)
    responses: List[Response] = field(default_factory=list)
    security: List[Dict[str, List[str]]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    deprecated: bool = False


@dataclass
class APISpec:
    """API规范定义"""

    title: str
    description: str
    version: str
    base_url: str
    host: str = "localhost"
    schemes: List[str] = field(default_factory=lambda: ["http"])
    consumes: List[str] = field(default_factory=list)
    produces: List[str] = field(default_factory=list)
    paths: Dict[str, Dict[str, PathItem]] = field(default_factory=dict)
    components: Dict[str, Any] = field(default_factory=dict)
    security_definitions: Dict[str, Any] = field(default_factory=dict)
    external_docs: Dict[str, str] = field(default_factory=dict)
    tags: List[Dict[str, str]] = field(default_factory=list)
    servers: List[Dict[str, str]] = field(default_factory=list)
    info: Dict[str, Any] = field(default_factory=dict)


class FastAPIParser:
    """FastAPI应用解析器"""

    def __init__(self):
        self.extractors = {
            "query": self._extract_query_params,
            "path": self._extract_path_params,
            "body": self._extract_request_body,
            "response": self._extract_responses,
            "security": self._extract_security,
            "tags": self._extract_tags,
        }
        self.type_mapping = {
            "str": "string",
            "int": "integer",
            "float": "number",
            "bool": "boolean",
            "datetime": "string",
            "date": "string",
            "List": "array",
            "Dict": "object",
            "Union": "object",
        }

    def parse_app(self, app: FastAPI) -> APISpec:
        """解析FastAPI应用"""
        spec = APISpec(
            title=app.title or "Generated API",
            description=app.description or "",
            version=app.version or "1.0.0",
            base_url="http://localhost:8000",
        )

        # 解析路由
        for route in app.routes:
            if hasattr(route, "path") and hasattr(route, "methods"):
                self._parse_route(spec, route)

        return spec

    def _parse_route(self, spec: APISpec, route):
        """解析单个路由"""
        path = route.path
        methods = [m.lower() for m in route.methods if m.lower() != "head"]

        # 解析路径参数
        path_params = self._extract_path_template_params(path)

        for method in methods:
            if hasattr(route, "endpoint") and route.endpoint:
                path_item = PathItem(
                    path=path,
                    method=method.upper(),
                    summary=getattr(route.endpoint, "__doc__", "") or "",
                    description=getattr(route.endpoint, "__doc__", "") or "",
                )

                # 解析函数签名
                signature = inspect.signature(route.endpoint)
                self._extract_parameters_from_signature(path_item, signature, path_params)

                spec.paths[path] = spec.paths.get(path, {})
                spec.paths[path][method.upper()] = path_item

    def _extract_path_template_params(self, path: str) -> List[Parameter]:
        """提取路径模板参数"""
        params = []
        for match in re.finditer(r"\{([^}]+)\}", path):
            param_name = match.group(1)
            param = Parameter(
                name=param_name,
                type="string",
                required=True,
                description=f"Path parameter {param_name}",
                default="",
                example="example",
            )
            params.append(param)
        return params

    def _extract_parameters_from_signature(
        self,
        path_item: PathItem,
        signature: inspect.Signature,
        path_params: List[Parameter],
    ):
        """从函数签名提取参数"""
        for param_name, param in signature.parameters.items():
            if param_name == "request":
                continue

            # 路径参数
            path_param = next((p for p in path_params if p.name == param_name), None)
            if path_param:
                path_item.parameters.append(path_param)
                continue

            # 查询参数
            annotation = param.annotation if param.annotation != inspect.Parameter.empty else str
            param_type = self._type_to_string(annotation)

            query_param = Parameter(
                name=param_name,
                type=param_type,
                required=param.default == inspect.Parameter.empty,
                description=f"Query parameter {param_name}",
                default=param.default if param.default != inspect.Parameter.empty else None,
            )
            path_item.parameters.append(query_param)

    def _type_to_string(self, type_annotation) -> str:
        """类型转换为字符串"""
        if type_annotation == inspect.Parameter.empty:
            return "string"
        if isinstance(type_annotation, str):
            return type_annotation
        if hasattr(type_annotation, "__name__"):
            return self.type_mapping.get(type_annotation.__name__, type_annotation.__name__)
        return "string"


class TypeAnalyzer:
    """类型分析器"""

    def __init__(self):
        self.type_cache = {}

    def analyze_pydantic_model(self, model_class: type) -> Dict[str, Any]:
        """分析Pydantic模型"""
        model_name = model_class.__name__
        cache_key = model_name

        if cache_key in self.type_cache:
            return self.type_cache[cache_key]

        schema = {"type": "object", "properties": {}, "required": []}

        # 分析字段
        for field_name, field_info in model_class.__fields__.items():
            field_schema = self._analyze_field_info(field_info)
            schema["properties"][field_name] = field_schema

            # 检查是否必需
            if not field_info.required:
                schema["required"].append(field_name)

        # 处理必需字段
        if schema["required"]:
            schema["required"] = list(schema["required"])

        # 设置引用
        schema["$ref"] = f"#/components/schemas/{model_name}"

        self.type_cache[cache_key] = schema
        return schema

    def _analyze_field_info(self, field_info: FieldInfo) -> Dict[str, Any]:
        """分析字段信息"""
        schema = {}

        # 类型映射
        field_type = field_info.type_
        if field_type.__name__ in self.type_mapping:
            schema["type"] = self.type_mapping[field_type.__name__]
        else:
            schema["type"] = "object"

        # 描述
        if field_info.description:
            schema["description"] = field_info.description

        # 默认值
        if field_info.default != FieldInfo.default_factory:
            schema["default"] = field_info.default

        # 示例
        if field_info.field_info and field_info.field_info.example:
            schema["example"] = field_info.field_info.example

        # 必需性
        schema["required"] = field_info.required

        # 枚举值
        if hasattr(field_type, "__origin__") and field_type.__origin__ == Union:
            schema["type"] = "object"

        # 字段验证
        if field_info.validator:
            schema["validators"] = self._extract_validators(field_info.validator)

        return schema

    @property
    def type_mapping(self):
        """类型映射"""
        return {
            "str": "string",
            "int": "integer",
            "float": "number",
            "bool": "boolean",
            "datetime": "string",
            "date": "string",
        }

    def _extract_validators(self, validator) -> List[Dict[str, Any]]:
        """提取验证器信息"""
        validators = []
        # 这里可以提取具体的验证规则
        return validators


class OpenAPISpecGenerator:
    """OpenAPI规范生成器"""

    def __init__(self):
        self.parser = FastAPIParser()
        self.analyzer = TypeAnalyzer()

    def generate_from_app(self, app: FastAPI) -> APISpec:
        """从FastAPI应用生成规范"""
        return self.parser.parse_app(app)

    def generate_from_file(self, file_path: str) -> APISpec:
        """从文件生成规范"""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.suffix.lower() == ".py":
            return self._generate_from_python_file(file_path)
        elif file_path.suffix.lower() in [".yaml", ".yml"]:
            return self._generate_from_yaml_file(file_path)
        elif file_path.suffix.lower() == ".json":
            return self._generate_from_json_file(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

    def _generate_from_python_file(self, file_path: Path) -> APISpec:
        """从Python文件生成规范"""
        import importlib.util

        spec = importlib.util.spec_from_file_location("module", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # 查找FastAPI应用
        if hasattr(module, "app"):
            return self.generate_from_app(module.app)
        else:
            raise ValueError("No FastAPI app found in the Python file")

    def _generate_from_yaml_file(self, file_path: Path) -> APISpec:
        """从YAML文件生成规范"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = yaml.safe_load(f)

        return self._convert_to_api_spec(content)

    def _generate_from_json_file(self, file_path: Path) -> APISpec:
        """从JSON文件生成规范"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = json.load(f)

        return self._convert_to_api_spec(content)

    def _convert_to_api_spec(self, content: Dict) -> APISpec:
        """转换为API规范对象"""
        spec = APISpec(
            title=content.get("info", {}).get("title", "Generated API"),
            description=content.get("info", {}).get("description", ""),
            version=content.get("info", {}).get("version", "1.0.0"),
            base_url=(
                content.get("servers", [{}])[0].get("url", "http://localhost:8000")
                if content.get("servers")
                else "http://localhost:8000"
            ),
        )

        # 转换路径
        if "paths" in content:
            for path, path_data in content["paths"].items():
                spec.paths[path] = {}
                for method, method_data in path_data.items():
                    path_item = PathItem(
                        path=path,
                        method=method.upper(),
                        summary=method_data.get("summary", ""),
                        description=method_data.get("description", ""),
                    )
                    spec.paths[path][method.upper()] = path_item

        # 转换组件
        if "components" in content:
            spec.components = content["components"]

        return spec

    def export_to_yaml(self, spec: APISpec, output_path: str):
        """导出为YAML格式"""
        content = self._api_spec_to_dict(spec)
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(content, f, default_flow_style=False, allow_unicode=True)

    def export_to_json(self, spec: APISpec, output_path: str):
        """导出为JSON格式"""
        content = self._api_spec_to_dict(spec)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=2, ensure_ascii=False)

    def _api_spec_to_dict(self, spec: APISpec) -> Dict:
        """转换API规范为字典"""
        content = {
            "openapi": "3.0.0",
            "info": {
                "title": spec.title,
                "description": spec.description,
                "version": spec.version,
            },
        }

        # 添加服务器
        if spec.servers:
            content["servers"] = spec.servers

        # 添加路径
        if spec.paths:
            content["paths"] = {}
            for path, methods in spec.paths.items():
                content["paths"][path] = {}
                for method, path_item in methods.items():
                    method_spec = {
                        "summary": path_item.summary,
                        "description": path_item.description,
                        "deprecated": path_item.deprecated,
                    }

                    # 添加参数
                    if path_item.parameters:
                        method_spec["parameters"] = []
                        for param in path_item.parameters:
                            param_spec = {
                                "name": param.name,
                                "in": "path" if "{" in path_item.path else "query",
                                "required": param.required,
                                "schema": {"type": param.type},
                            }
                            if param.description:
                                param_spec["description"] = param.description
                            if param.default is not None:
                                param_spec["schema"]["default"] = param.default
                            method_spec["parameters"].append(param_spec)

                    content["paths"][path][method.lower()] = method_spec

        # 添加组件
        if spec.components:
            content["components"] = spec.components

        return content


class ContractGenerator:
    """契约生成器主类"""

    def __init__(self, validation_level: ValidationLevel = ValidationLevel.MODERATE):
        self.generator = OpenAPISpecGenerator()
        self.validation_level = validation_level
        self.history = []

    def generate_contract(
        self,
        source_type: ContractSourceType,
        source_path: str,
        output_format: str = "yaml",
        output_path: Optional[str] = None,
    ) -> APISpec:
        """生成契约"""
        start_time = time.time()

        try:
            # 根据源类型生成规范
            if source_type == ContractSourceType.FASTAPI:
                # 这里需要传入FastAPI应用实例
                spec = self._generate_from_fastapi_app(source_path)
            elif source_type == ContractSourceType.FASTAPI_FILE:
                spec = self.generator.generate_from_file(source_path)
            elif source_type == ContractSourceType.AUTO_DETECT:
                spec = self._auto_detect_and_generate(source_path)
            else:
                spec = self.generator.generate_from_file(source_path)

            # 验证规范
            self._validate_spec(spec)

            # 导出结果
            if output_path:
                self._export_spec(spec, output_format, output_path)

            # 记录历史
            end_time = time.time()
            history_entry = {
                "timestamp": datetime.now().isoformat(),
                "source_type": source_type.value,
                "source_path": source_path,
                "output_format": output_format,
                "output_path": output_path,
                "duration": end_time - start_time,
                "success": True,
                "paths_count": len(spec.paths),
            }
            self.history.append(history_entry)

            print(f"✓ 契约生成成功: {spec.title} v{spec.version}")
            print(f"  路径数: {len(spec.paths)}")
            print(f"  耗时: {end_time - start_time:.2f}秒")

            return spec

        except Exception as e:
            end_time = time.time()
            history_entry = {
                "timestamp": datetime.now().isoformat(),
                "source_type": source_type.value,
                "source_path": source_path,
                "output_format": output_format,
                "output_path": output_path,
                "duration": end_time - start_time,
                "success": False,
                "error": str(e),
            }
            self.history.append(history_entry)

            print(f"❌ 契约生成失败: {e}")
            raise

    def _generate_from_fastapi_app(self, app: FastAPI) -> APISpec:
        """从FastAPI应用生成规范"""
        return self.generator.generate_from_app(app)

    def _auto_detect_and_generate(self, source_path: str) -> APISpec:
        """自动检测并生成规范"""
        file_path = Path(source_path)

        if file_path.suffix.lower() == ".py":
            # 尝试导入并查找FastAPI应用
            spec = self.generator.generate_from_file(str(file_path))
            if spec.paths:
                return spec
            else:
                raise ValueError("未找到FastAPI应用或路径定义")

        elif file_path.suffix.lower() in [".yaml", ".yml", ".json"]:
            return self.generator.generate_from_file(str(file_path))

        else:
            raise ValueError(f"无法识别的文件类型: {file_path.suffix}")

    def _validate_spec(self, spec: APISpec):
        """验证规范"""
        errors = []

        # 基础验证
        if not spec.title:
            errors.append("缺少API标题")

        if not spec.version:
            errors.append("缺少API版本")

        if not spec.paths:
            errors.append("缺少路径定义")

        # 根据验证级别进行严格验证
        if self.validation_level == ValidationLevel.STRICT:
            # 严格验证
            if len(spec.paths) == 0:
                errors.append("至少需要定义一个路径")

            for path, methods in spec.paths.items():
                if not methods:
                    errors.append(f"路径 {path} 没有定义任何方法")

                for method, path_item in methods.items():
                    if not path_item.responses:
                        errors.append(f"路径 {path} 方法 {method} 没有定义响应")
        elif self.validation_level == ValidationLevel.MODERATE:
            # 中等验证
            for path, methods in spec.paths.items():
                for method, path_item in methods.items():
                    if not path_item.responses and self.validation_level == ValidationLevel.MODERATE:
                        path_item.responses.append(Response(status_code=200, description="成功响应"))

        if errors:
            error_msg = "契约验证失败:\n" + "\n".join(f"  - {error}" for error in errors)
            if self.validation_level == ValidationLevel.LENIENT:
                print(f"⚠️  {error_msg}")
            else:
                raise ValueError(error_msg)

    def _export_spec(self, spec: APISpec, format: str, output_path: str):
        """导出规范"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format.lower() == "yaml":
            self.generator.export_to_yaml(spec, str(output_path))
        elif format.lower() == "json":
            self.generator.export_to_json(spec, str(output_path))
        else:
            raise ValueError(f"不支持的输出格式: {format}")

        print(f"✓ 契约已导出: {output_path}")

    def get_generation_history(self) -> List[Dict[str, Any]]:
        """获取生成历史"""
        return self.history.copy()

    def analyze_api_complexity(self, spec: APISpec) -> Dict[str, Any]:
        """分析API复杂度"""
        complexity_metrics = {
            "total_paths": len(spec.paths),
            "total_methods": sum(len(methods) for methods in spec.paths.values()),
            "avg_parameters_per_method": 0,
            "avg_responses_per_method": 0,
            "most_used_method": "",
            "path_complexity": {},
        }

        total_parameters = 0
        total_responses = 0
        method_counts = {}

        for path, methods in spec.paths.items():
            method_count = len(methods)
            complexity_metrics["path_complexity"][path] = {
                "method_count": method_count,
                "parameters": 0,
                "responses": 0,
            }

            for method, path_item in methods.items():
                total_parameters += len(path_item.parameters)
                total_responses += len(path_item.responses)
                method_counts[method] = method_counts.get(method, 0) + 1

                complexity_metrics["path_complexity"][path]["parameters"] += len(path_item.parameters)
                complexity_metrics["path_complexity"][path]["responses"] += len(path_item.responses)

        if total_methods > 0:
            complexity_metrics["avg_parameters_per_method"] = total_parameters / total_methods
            complexity_metrics["avg_responses_per_method"] = total_responses / total_methods

        if method_counts:
            complexity_metrics["most_used_method"] = max(method_counts, key=method_counts.get)

        return complexity_metrics


# 使用示例
def demo_contract_generator():
    """演示契约生成器功能"""
    print("🚀 演示契约生成器功能")

    # 创建生成器
    generator = ContractGenerator(validation_level=ValidationLevel.MODERATE)

    # 模拟一个简单的FastAPI应用
    from fastapi import FastAPI

    class Item(BaseModel):
        name: str
        price: float
        description: Optional[str] = None

    demo_app = FastAPI(title="Demo API", version="1.0.0")

    @demo_app.get("/items/{item_id}")
    async def read_item(item_id: int, q: Optional[str] = None):
        """获取项目详情"""
        return {"item_id": item_id, "q": q}

    @demo_app.post("/items/")
    async def create_item(item: Item):
        """创建新项目"""
        return {"item": item, "status": "created"}

    # 生成契约
    try:
        spec = generator.generate_contract(
            source_type=ContractSourceType.FASTAPI,
            source_path=demo_app,
            output_format="yaml",
            output_path="demo_contract.yaml",
        )

        # 分析复杂度
        complexity = generator.analyze_api_complexity(spec)
        print(f"\n📊 API复杂度分析: {complexity}")

        print("\n✅ 契约生成演示完成")

    except Exception as e:
        print(f"❌ 演示失败: {e}")


if __name__ == "__main__":
    demo_contract_generator()

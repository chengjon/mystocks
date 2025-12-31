import sys
import os
import json
import yaml
import argparse

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
backend_path = os.path.join(project_root, 'web', 'backend')
sys.path.insert(0, project_root)
sys.path.insert(0, backend_path)

def generate_spec(tag_filter=None, output_file=None):
    try:
        # Import app
        # We need to mock some environment variables if necessary
        os.environ.setdefault("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mystocks")
        os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

        from app.main import app
        from fastapi.openapi.utils import get_openapi

        schema = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes,
        )

        if tag_filter:
            filtered_paths = {}
            for path, methods in schema["paths"].items():
                new_methods = {}
                for method, details in methods.items():
                    if "tags" in details and tag_filter in details["tags"]:
                        new_methods[method] = details

                if new_methods:
                    filtered_paths[path] = new_methods

            schema["paths"] = filtered_paths
            # Note: We are keeping all components schemas to avoid missing references.
            # A cleaner implementation would tree-shake unused schemas.

        output = output_file or "openapi.yaml"
        with open(output, "w", encoding="utf-8") as f:
            if output.endswith(".json"):
                json.dump(schema, f, indent=2, ensure_ascii=False)
            else:
                yaml.dump(schema, f, sort_keys=False, allow_unicode=True)

        print(f"Generated spec for tag '{tag_filter}' to {output}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", help="Filter by tag")
    parser.add_argument("--output", help="Output file")
    args = parser.parse_args()

    generate_spec(args.tag, args.output)

#!/usr/bin/env python3
"""
Slow Query Analyzer and Index Optimization Tool
Analyzes query patterns and suggests index improvements
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class QueryPattern:
    """Represent a query pattern"""
    query_type: str
    table: str
    columns: List[str] = field(default_factory=list)
    where_columns: List[str] = field(default_factory=list)
    order_columns: List[str] = field(default_factory=list)
    join_columns: List[str] = field(default_factory=list)
    frequency: int = 0
    avg_duration_ms: float = 0.0
    has_wildcard: bool = False
    has_like_prefix: bool = False
    has_or_condition: bool = False


class SlowQueryAnalyzer:
    """Analyzer for slow queries and index suggestions"""

    def __init__(self):
        self.query_patterns: Dict[str, QueryPattern] = {}
        self.index_suggestions: List[Dict] = []
        self._load_common_patterns()

    def _load_common_patterns(self):
        """Load common query patterns"""

    def analyze_query(self, query: str, duration_ms: float) -> Optional[QueryPattern]:
        """Analyze a single query and return pattern"""
        query = query.strip().lower()

        if not query:
            return None

        pattern = QueryPattern(
            query_type=self._extract_query_type(query),
            table=self._extract_table(query),
            avg_duration_ms=duration_ms,
            frequency=1,
        )

        pattern.columns = self._extract_columns(query)
        pattern.where_columns = self._extract_where_columns(query)
        pattern.order_columns = self._extract_order_columns(query)
        pattern.join_columns = self._extract_join_columns(query)

        pattern.has_wildcard = "*" in query and "select" in query
        pattern.has_like_prefix = self._has_leading_wildcard_like(query)
        pattern.has_or_condition = " or " in query and "union" not in query

        key = f"{pattern.table}_{pattern.query_type}"
        if key in self.query_patterns:
            existing = self.query_patterns[key]
            existing.frequency += 1
            existing.avg_duration_ms = (
                (existing.avg_duration_ms * (existing.frequency - 1) + duration_ms)
                / existing.frequency
            )
        else:
            self.query_patterns[key] = pattern

        return pattern

    def _extract_query_type(self, query: str) -> str:
        """Extract query type (SELECT, INSERT, UPDATE, DELETE)"""
        match = re.match(r'^\s*(select|insert|update|delete)\s+', query)
        if match:
            return match.group(1).upper()
        return "UNKNOWN"

    def _extract_table(self, query: str) -> str:
        """Extract main table name"""
        patterns = [
            r'\bfrom\s+(\w+)',
            r'\binto\s+(\w+)',
            r'\bupdate\s+(\w+)',
            r'\bdelete\s+from\s+(\w+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                table = match.group(1)
                if table not in ('where', 'order', 'limit'):
                    return table
        return "unknown"

    def _extract_columns(self, query: str) -> List[str]:
        """Extract selected/updated columns"""
        if "select" in query:
            match = re.search(r'select\s+(.+?)\s+from', query, re.IGNORECASE | re.DOTALL)
            if match:
                cols = re.findall(r'(\w+)', match.group(1))
                return [c for c in cols if c not in ('select', 'distinct', 'count', 'sum', 'avg', 'max', 'min')]
        return []

    def _extract_where_columns(self, query: str) -> List[str]:
        """Extract columns used in WHERE clause"""
        match = re.search(r'where\s+(.+?)(?:\s+order\s+|\s+group\s+|\s+limit\s+|$)', query, re.IGNORECASE | re.DOTALL)
        if match:
            where_clause = match.group(1)
            cols = re.findall(r'(\w+)\s*(?:=|>|<|>=|<=|!=|<>|like|ilike|in|between)', where_clause)
            return list(set(cols))
        return []

    def _extract_order_columns(self, query: str) -> List[str]:
        """Extract columns used in ORDER BY"""
        match = re.search(r'order\s+by\s+(.+?)(?:\s+limit\s+|$)', query, re.IGNORECASE)
        if match:
            cols = re.findall(r'(\w+)', match.group(1))
            return list(set(cols))
        return []

    def _extract_join_columns(self, query: str) -> List[str]:
        """Extract columns used in JOINs"""
        matches = re.findall(r'join\s+\w+\s+on\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)', query, re.IGNORECASE)
        cols = []
        for m in matches:
            cols.extend([m[1], m[3]])
        return list(set(cols))

    def _has_leading_wildcard_like(self, query: str) -> bool:
        """Check for LIKE patterns with leading wildcard"""
        return bool(re.search(r'like\s+[\'"]%', query, re.IGNORECASE))

    def generate_index_suggestions(self) -> List[Dict]:
        """Generate index optimization suggestions"""
        suggestions = []

        for key, pattern in self.query_patterns.items():
            if pattern.avg_duration_ms > 50:  # Only suggest for slow queries
                suggestion = {
                    "table": pattern.table,
                    "index_type": "BTREE",
                    "columns": [],
                    "reason": "",
                    "priority": "medium",
                    "query_count": pattern.frequency,
                    "avg_duration_ms": round(pattern.avg_duration_ms, 2),
                }

                where_cols = [c for c in pattern.where_columns if c not in pattern.columns]

                if where_cols:
                    suggestion["columns"] = where_cols
                    suggestion["reason"] = "Frequently used in WHERE clause"
                    suggestion["priority"] = "high" if pattern.avg_duration_ms > 200 else "medium"
                    suggestions.append(suggestion)

                if pattern.order_columns:
                    if pattern.order_columns[0] not in suggestion["columns"]:
                        suggestion["columns"] = pattern.order_columns + suggestion["columns"]
                        suggestion["reason"] = "Used in ORDER BY for faster sorting"
                        suggestions.append(suggestion)

                if pattern.has_like_prefix:
                    suggestion["columns"] = [pattern.where_columns[0]] if pattern.where_columns else []
                    suggestion["reason"] = "LIKE with leading wildcard - consider full-text search"
                    suggestion["priority"] = "low"
                    suggestions.append(suggestion)

                if pattern.has_or_condition:
                    suggestion["columns"] = [c for c in pattern.where_columns if c not in suggestion.get("columns", [])]
                    suggestion["reason"] = "Multiple OR conditions - consider IN clause or composite index"
                    suggestions.append(suggestion)

        return suggestions

    def get_summary(self) -> Dict:
        """Get analysis summary"""
        slow_queries = {k: v for k, v in self.query_patterns.items() if v.avg_duration_ms > 100}

        return {
            "total_patterns": len(self.query_patterns),
            "slow_patterns": len(slow_queries),
            "total_queries_analyzed": sum(p.frequency for p in self.query_patterns.values()),
            "avg_duration_ms": round(
                sum(p.avg_duration_ms * p.frequency for p in self.query_patterns.values()) /
                max(sum(p.frequency for p in self.query_patterns.values()), 1),
                2
            ),
            "suggestions_count": len(self.generate_index_suggestions()),
        }


class IndexRecommendationGenerator:
    """Generate SQL for index recommendations"""

    POSTGRESQL_HEADER = """-- PostgreSQL Index Recommendations
-- Generated by Slow Query Analyzer
-- Run these in PostgreSQL to optimize query performance
-- Note: Review each index before execution
"""

    def generate_postgresql_indexes(self, suggestions: List[Dict]) -> str:
        """Generate PostgreSQL CREATE INDEX statements"""
        output = [self.POSTGRESQL_HEADER]
        seen = set()

        for sugg in suggestions:
            index_name = f"idx_{sugg['table']}_{'_'.join(sugg['columns'][:3])}"[:63]
            if index_name in seen:
                continue
            seen.add(index_name)

            columns_str = ", ".join(sugg["columns"])

            sql = f"""
-- {sugg['reason']}
-- Priority: {sugg['priority']}
-- Estimated improvement: {sugg['avg_duration_ms']:.0f}ms -> {(sugg['avg_duration_ms'] * 0.3):.0f}ms
CREATE INDEX IF NOT EXISTS {index_name}
ON {sugg['table']} USING {sugg['index_type']} ({columns_str});
"""
            output.append(sql)

        return "\n".join(output)

    def generate_tdengine_indexes(self, suggestions: List[Dict]) -> str:
        """Generate TDengine-specific index recommendations"""
        output = ["""-- TDengine Index Recommendations
-- Note: TDengine uses time-based partitioning
-- Focus on timestamp columns and tag indexes
"""]

        for sugg in suggestions:
            columns_str = ", ".join(sugg["columns"])

            sql = f"""
-- {sugg['reason']}
-- Note: TDengine may not need traditional B-tree indexes
-- Consider using TAGS for filtering if columns are tags
CREATE STABLE IF NOT EXISTS {sugg['table']}_optimized
(...);
"""
            output.append(sql)

        return "\n".join(output)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Slow Query Analyzer")
    parser.add_argument("--analyze", "-a", help="Query log file to analyze")
    parser.add_argument("--generate-indexes", "-g", action="store_true", help="Generate index SQL")
    parser.add_argument("--output", "-o", default="index_recommendations.sql", help="Output file")

    args = parser.parse_args()

    analyzer = SlowQueryAnalyzer()
    generator = IndexRecommendationGenerator()

    if args.analyze:
        with open(args.analyze, 'r') as f:
            for line in f:
                try:
                    import json
                    log = json.loads(line.strip())
                    analyzer.analyze_query(
                        log.get("query", ""),
                        log.get("duration_ms", 0)
                    )
                except (json.JSONDecodeError, KeyError):
                    continue

    summary = analyzer.get_summary()
    print("Analysis Summary:")
    print(f"  Total patterns: {summary['total_patterns']}")
    print(f"  Slow patterns: {summary['slow_patterns']}")
    print(f"  Suggestions: {summary['suggestions_count']}")

    if args.generate_indexes:
        suggestions = analyzer.generate_index_suggestions()
        sql = generator.generate_postgresql_indexes(suggestions)
        with open(args.output, 'w') as f:
            f.write(sql)
        print(f"Index recommendations written to {args.output}")


if __name__ == "__main__":
    main()

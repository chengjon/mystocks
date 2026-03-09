#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


SCENARIO = sys.argv[1]
LOG_PATH = Path(sys.argv[2])
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

turn_counter = 0


def log(message: str) -> None:
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(f"{message}\n")


def send(message: dict) -> None:
    sys.stdout.write(json.dumps(message) + "\n")
    sys.stdout.flush()


def read_message() -> dict:
    line = sys.stdin.readline()
    if not line:
        raise SystemExit(0)
    return json.loads(line)


def respond(request_id, result: dict) -> None:
    send({"jsonrpc": "2.0", "id": request_id, "result": result})


def wait_for_client_response(expected_id: str) -> dict:
    while True:
        message = read_message()
        if "method" in message:
            log(f"unexpected:{message['method']}")
            continue
        if message.get("id") == expected_id:
            return message


while True:
    message = read_message()

    if "method" in message:
        method = message["method"]
        log(method)

        if method == "initialize":
            respond(message["id"], {"capabilities": {}})
            continue

        if method == "initialized":
            continue

        if method == "thread/start":
            dynamic_tools = (((message.get("params") or {}).get("config") or {}).get("dynamic_tools")) or []
            if dynamic_tools:
                log(f"dynamic_tools:{','.join(tool.get('name', '') for tool in dynamic_tools)}")
            respond(
                message["id"],
                {
                    "approvalPolicy": "never",
                    "cwd": message["params"].get("cwd", ""),
                    "model": "gpt-5.3-codex",
                    "modelProvider": "openai",
                    "sandbox": {"type": "workspace-write"},
                    "thread": {"id": "thread-1"},
                },
            )
            continue

        if method == "turn/start":
            turn_counter += 1
            turn_id = f"turn-{turn_counter}"
            respond(message["id"], {"turn": {"id": turn_id}})
            send(
                {
                    "jsonrpc": "2.0",
                    "method": "thread/tokenUsage/updated",
                    "params": {
                        "threadId": "thread-1",
                        "turnId": turn_id,
                        "tokenUsage": {
                            "last": {
                                "cachedInputTokens": 0,
                                "inputTokens": 3,
                                "outputTokens": 2,
                                "reasoningOutputTokens": 0,
                                "totalTokens": 5,
                            },
                            "total": {
                                "cachedInputTokens": 0,
                                "inputTokens": 3 * turn_counter,
                                "outputTokens": 2 * turn_counter,
                                "reasoningOutputTokens": 0,
                                "totalTokens": 5 * turn_counter,
                            },
                        },
                    },
                }
            )

            if SCENARIO == "success":
                send(
                    {
                        "jsonrpc": "2.0",
                        "method": "turn/completed",
                        "params": {"threadId": "thread-1", "turnId": turn_id},
                    }
                )
                continue

            if SCENARIO == "approval_and_tool":
                send(
                    {
                        "jsonrpc": "2.0",
                        "id": "approval-1",
                        "method": "exec/approval",
                        "params": {
                            "type": "exec_approval_request",
                            "call_id": "cmd-1",
                            "approval_id": "approval-1",
                            "command": ["echo", "hello"],
                            "cwd": message["params"].get("cwd", ""),
                        },
                    }
                )
                approval_response = wait_for_client_response("approval-1")
                log(f"approval:{approval_response['result']['decision']}")

                send(
                    {
                        "jsonrpc": "2.0",
                        "id": "tool-1",
                        "method": "dynamic_tool_call",
                        "params": {
                            "type": "dynamic_tool_call_request",
                            "tool": "unknown_tool",
                            "callId": "call-1",
                            "turnId": turn_id,
                            "arguments": {"value": 1},
                        },
                    }
                )
                tool_response = wait_for_client_response("tool-1")
                log(f"tool:{tool_response['result'].get('error')}")
                send(
                    {
                        "jsonrpc": "2.0",
                        "method": "turn/completed",
                        "params": {"threadId": "thread-1", "turnId": turn_id},
                    }
                )
                continue

            if SCENARIO == "supported_tool":
                send(
                    {
                        "jsonrpc": "2.0",
                        "id": "tool-1",
                        "method": "dynamic_tool_call",
                        "params": {
                            "type": "dynamic_tool_call_request",
                            "tool": "linear_graphql",
                            "callId": "call-1",
                            "threadId": "thread-1",
                            "turnId": turn_id,
                            "arguments": {
                                "query": "query Projects { projects { nodes { id name } } }",
                                "variables": {"limit": 1},
                            },
                        },
                    }
                )
                tool_response = wait_for_client_response("tool-1")
                log(f"tool_success:{tool_response['result']['success']}")
                content_items = tool_response["result"].get("contentItems") or []
                if content_items:
                    log(f"tool_text:{content_items[0]['text']}")
                send(
                    {
                        "jsonrpc": "2.0",
                        "method": "turn/completed",
                        "params": {"threadId": "thread-1", "turnId": turn_id},
                    }
                )
                continue

            if SCENARIO == "request_user_input":
                send(
                    {
                        "jsonrpc": "2.0",
                        "method": "event",
                        "params": {
                            "type": "request_user_input",
                            "call_id": "input-1",
                            "questions": [],
                            "turn_id": turn_id,
                        },
                    }
                )
                continue

            if SCENARIO == "multi_turn":
                send(
                    {
                        "jsonrpc": "2.0",
                        "method": "turn/completed",
                        "params": {"threadId": "thread-1", "turnId": turn_id},
                    }
                )
                continue

    else:
        log(f"response:{message.get('id')}")

#!/usr/bin/env bash

port_is_listening() {
  ss -ltnH "( sport = :$1 )" 2>/dev/null | grep -q .
}

resolve_frontend_port() {
  local preferred="$1"
  local backup="$2"
  local was_set="$3"

  if [ -n "${was_set}" ]; then
    printf '%s' "${preferred}"
    return 0
  fi

  if port_is_listening "${preferred}" && ! port_is_listening "${backup}"; then
    printf '%s' "${backup}"
    return 0
  fi

  printf '%s' "${preferred}"
}

resolve_backend_target_port() {
  local preferred="$1"
  printf '%s' "${preferred}"
}

resolve_backend_spawn_port() {
  local preferred="$1"
  local backup="$2"
  local was_set="$3"

  if [ -n "${was_set}" ]; then
    printf '%s' "${preferred}"
    return 0
  fi

  if ! port_is_listening "${preferred}"; then
    printf '%s' "${preferred}"
    return 0
  fi

  if ! port_is_listening "${backup}"; then
    printf '%s' "${backup}"
    return 0
  fi

  printf '%s' "${preferred}"
}

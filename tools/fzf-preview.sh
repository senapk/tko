#!/usr/bin/env bash

set -euo pipefail

index_file="/tmp/fzf_snapshots"
yellow=$'\033[33m'
green=$'\033[32m'
blue=$'\033[34m'
reset=$'\033[0m'

build_snapshot() {
  if (( $# > 0 )); then
    printf '%s\n' "$@" > "$index_file"
    return 0
  fi

  find . -type f | sort > "$index_file"
}

resolve_context_args() {
  local mode="$1"
  case "$mode" in
    diff)
      DIFF_CONTEXT_ARGS=(-U10)
      ;;
    wide)
      DIFF_CONTEXT_ARGS=(-U40)
      ;;
    full)
      DIFF_CONTEXT_ARGS=(-U999999 --inter-hunk-context=999999)
      ;;
    *)
      DIFF_CONTEXT_ARGS=(-U10)
      ;;
  esac
}

extract_epoch_from_snapshot_name() {
  local file_path="$1"
  local base_name
  local yyyy
  local mm
  local dd
  local hh
  local mi
  local ss
  local stamp

  base_name="$(basename -- "$file_path")"
  if [[ "$base_name" =~ ^([0-9]{4})-([0-9]{2})-([0-9]{2})_([0-9]{2})-([0-9]{2})-([0-9]{2})_ ]]; then
    yyyy="${BASH_REMATCH[1]}"
    mm="${BASH_REMATCH[2]}"
    dd="${BASH_REMATCH[3]}"
    hh="${BASH_REMATCH[4]}"
    mi="${BASH_REMATCH[5]}"
    ss="${BASH_REMATCH[6]}"
    stamp="$yyyy-$mm-$dd $hh:$mi:$ss"
    date -d "$stamp" +%s 2>/dev/null || return 1
    return 0
  fi

  return 1
}

format_elapsed() {
  local total_seconds="$1"
  local days=$((total_seconds / 86400))
  local hours=$(((total_seconds % 86400) / 3600))
  local minutes=$(((total_seconds % 3600) / 60))
  local seconds=$((total_seconds % 60))

  if (( days > 0 )); then
    printf '%dd %02d:%02d:%02d' "$days" "$hours" "$minutes" "$seconds"
  else
    printf '%02d:%02d:%02d' "$hours" "$minutes" "$seconds"
  fi
}

print_blue_rule() {
  local width="$1"
  local rule

  printf -v rule '%*s' "$width" ''
  rule="${rule// /─}"
  printf '%b\n' "${blue}${rule}${reset}"
}

render_elapsed_line() {
  local idx="$1"
  local current="$2"
  local prev="${3:-}"

  if (( idx <= 1 )); then
    printf '%s' '--:--:--'
    return 0
  fi

  local current_epoch
  local prev_epoch
  if current_epoch="$(extract_epoch_from_snapshot_name "$current")" && prev_epoch="$(extract_epoch_from_snapshot_name "$prev")"; then
    local elapsed_seconds=$((current_epoch - prev_epoch))
    if (( elapsed_seconds < 0 )); then
      elapsed_seconds=$((-elapsed_seconds))
    fi
    printf '%s' "$(format_elapsed "$elapsed_seconds")"
  else
    printf '%s' '--:--:--'
  fi
}

render_preview() {
  local idx="$1"
  local mode="${2:-diff}"
  local preview_cols="${FZF_PREVIEW_COLUMNS:-120}"
  local shortcuts='Alt+[1:diff | 2:wide | 3:full], Left:Previous, Right:Next'

  mapfile -t files < "$index_file"
  if [[ ! "$idx" =~ ^[0-9]+$ ]] || (( idx < 1 || idx > ${#files[@]} )); then
    echo "Indice invalido"
    return 0
  fi

  local current="${files[$((idx - 1))]}"
  local prev=""
  if (( idx > 1 )); then
    prev="${files[$((idx - 2))]}"
  fi

  resolve_context_args "$mode"
  local elapsed_display
  elapsed_display="$(render_elapsed_line "$idx" "$current" "$prev")"

  printf '%b\n' "${yellow}Elapsed=${green}${elapsed_display}${yellow} | Mode=${green}${mode}${yellow} | Shortcuts=${green}${shortcuts}${reset}"

  if (( idx == 1 )); then
    printf '%b\n' "${blue}$current${reset}"
  else
    printf '%b\n' "${blue}$prev ${green} -> ${blue}$current${reset}"
  fi
  print_blue_rule "$preview_cols"

  if (( idx > 1 )); then
    git diff --no-index "${DIFF_CONTEXT_ARGS[@]}" "$prev" "$current" | \
      delta \
        --paging=never \
        --side-by-side \
        --line-numbers \
        --tabs=4 \
        --width="$preview_cols" | \
        tail -n +6
  else
    printf '\n\n'
    
    bat \
      --color=always \
      --tabs=4 \
      --terminal-width="$preview_cols" \
      "$current" | \
        tail -n +4
  fi
}

run_fzf() {
  build_snapshot "$@"

  nl -ba "$index_file" | \
    fzf \
      --height=100% \
      --layout=reverse \
      --border=none \
      --list-border=sharp \
      --ansi \
      --info=inline \
      --delimiter=$'\t' \
      --with-nth=2.. \
      --preview "$0 --preview {1} diff" \
      --preview-window=down:80%:noborder \
      --bind 'left:up,right:down' \
      --bind 'up:preview-up,down:preview-down' \
      --bind 'pgup:preview-page-up,pgdn:preview-page-down' \
      --bind "alt-1:change-preview($0 --preview {1} diff)" \
      --bind "alt-2:change-preview($0 --preview {1} wide)" \
      --bind "alt-3:change-preview($0 --preview {1} full)"
}

main() {
  if [[ "${1:-}" == "--preview" ]]; then
    render_preview "${2:-0}" "${3:-diff}"
    return 0
  fi

  run_fzf "$@"
}

main "$@"
  
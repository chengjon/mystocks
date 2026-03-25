Amp CLI


COMMAND: amp --help

Usage: amp [options] [command]

Commands:

  logout       Log out by removing stored API key
  login        Log in to Amp
  threads      [alias: t, thread] Manage threads
    new        [alias: n] Create a new thread
    continue   [alias: c] Continue an existing thread
    list       [alias: l, ls] List all threads
    search     [alias: find] Search threads
    share      [alias: s] Share a thread
    rename     [alias: r] Rename a thread
    archive    Archive a thread
    delete     Delete a thread
    handoff    [alias: h] Create a handoff thread from an existing thread
    markdown   [alias: md] Render thread as markdown
    replay     [alias: p] Replay a thread
  tools        [alias: tool] Tool management commands
    list       [alias: ls] List all active tools (including MCP tools)
    show       Show details about an active tool
    make       Sets up a skeleton tool in your toolbox
    use        Invoke a tool with arguments or JSON input from stdin
  tasks        [alias: task] Task management commands
    import     Import tasks from a JSON file
    list       List tasks
  review       Run a code review on uncommitted changes or a commit range
  skill        [alias: skills] Manage skills from GitHub or local sources
    add        Install skills from a source
    list       [alias: ls] List all available skills
    remove     [alias: rm] Remove an installed skill
    info       Show information about a skill
  permissions  [alias: permission] Manage permissions
    list       [alias: ls] List permissions
    test       Test permissions
    edit       Edit permissions
    add        Add permission rule
  mcp          Manage MCP servers
    add        Add an MCP server configuration
    list       List all MCP server configurations
    remove     Remove an MCP server configuration
    oauth      Manage OAuth authentication for MCP servers
      login    Register OAuth client credentials for an MCP server
      logout   Remove OAuth credentials for an MCP server
      status   Show OAuth status for an MCP server
    doctor     Check MCP server status
    approve    Approve a workspace MCP server
  usage        Show your current Amp usage and credit balance
  update       Update Amp CLI

Options:

  --visibility <visibility>
      Set thread visibility (private, public, workspace, group)
  -V, --version
      Print the version number and exit
  --notifications
      Enable sound notifications (enabled by default when not in execute mode)
  --no-notifications
      Disable sound notifications (enabled by default when not in execute mode)
  --color
      Enable color output (enabled by default if stdout and stderr are sent to a TTY)
  --no-color
      Disable color output (enabled by default if stdout and stderr are sent to a TTY)
  --settings-file <value>
      Custom settings file path (overrides the default location /root/.config/amp/settings.json)
  --log-level <value>
      Set log level (error, warn, info, debug, audit)
  --log-file <value>
      Set log file location (overrides the default location /root/.cache/amp/logs/cli.log)
  --dangerously-allow-all
      Disable all command confirmation prompts (agent will execute all commands without asking)
  --jetbrains
      Enable JetBrains integration. When enabled, Amp automatically includes your open JetBrains file and text selection with every message.
  --no-jetbrains
      Disable JetBrains integration
  --ide
      Enable IDE connection (default). When enabled, Amp automatically includes your open IDE's file and text selection with every message.
  --no-ide
      Disable IDE connection
  --mcp-config <value>
      JSON configuration or file path for MCP servers to merge with existing settings
  -m, --mode <value>
      Set the agent mode (deep, free, rush, smart) — controls the model, system prompt, and tool selection
  -x, --execute [message]
      Use execute mode, optionally with user message. In execute mode, agent will execute provided prompt (either as argument, or via stdin). Only
      last assistant message is printed. Enabled automatically when redirecting stdout.
  --stream-json
      When used with --execute, output in Claude Code-compatible stream JSON format instead of plain text.
  --stream-json-thinking
      Include thinking blocks in stream JSON output (non-Claude Code extension). Implies --stream-json.
  --stream-json-input
      Read JSON Lines user messages from stdin. Requires both --execute and --stream-json.
  -l, --label <label>
      When used with --execute, add a label to the thread. Can be used multiple times.

Environment variables:

  AMP_API_KEY        Access token for Amp (see https://ampcode.com/settings)
  AMP_URL            URL for the Amp service (default is https://ampcode.com/)
  AMP_LOG_LEVEL      Set log level (can also use --log-level)
  AMP_LOG_FILE       Set log file location (can also use --log-file)
  AMP_SETTINGS_FILE  Set settings file path (can also use --settings-file, default: /root/.config/amp/settings.json)

Examples:

Start an interactive session:

  $ amp

Start an interactive session with a user message:

  $ echo "commit all my unstaged changes" | amp

Use execute mode (--execute or -x) to send a command to an agent, have it execute it, print only the agent's last message, and then exit:

  $ amp -x "what file in this folder is in markdown format?"
  All Markdown files in this folder:
  - README.md (root)
  - AGENT.md (root)
  - Documentation (7 files in doc/)
  - Various README.md files in subdirectories
  Total: **13 Markdown files** found across the project.

Stream JSON output and extract assistant text blocks with jq:

  $ amp -x "what file in this folder is in markdown format?" --stream-json | jq -r 'select(.type=="assistant") | .message.content[] | select(.type=="text") | .text'

Stream JSON output with thinking blocks and extract them with jq:

  $ amp -x "what file in this folder is in markdown format?" --stream-json-thinking | jq -r 'select(.type=="assistant") | .message.content[] | select(.type=="thinking") | .thinking'

Use execute mode and allow agent to use tools that would require approval:

  $ amp --dangerously-allow-all -x "Rename all .markdown files to .md. Only print list of renamed files."
  - readme.markdown → readme.md
  - ghostty.markdown → ghostty.md

Pipe a command to the agent and use execute mode:

  $ echo "commit all my unstaged changes" | amp -x --dangerously-allow-all
  Done. I have committed all your unstaged changes.

Pipe data to the agent and send along a prompt in execute mode:

  $ cat ~/.zshrc | amp -x "what does the 'beautiful' function do?"
  The `beautiful` function creates an infinite loop that prints the letter "o" in cycling colors every 0.2 seconds.

Execute a prompt from a file and store final assistant message output in a file (redirecting stdout is equivalent to providing -x/--execute):

  $ amp < prompt.txt > output.txt

Add an MCP server with a local command:

  $ amp mcp add context7 -- npx -y @upstash/context7-mcp

Add an MCP server with environment variables:

  $ amp mcp add postgres --env PGUSER=orb -- npx -y @modelcontextprotocol/server-postgres postgresql://localhost/orbing

Add a remote MCP server:

  $ amp mcp add hugging-face https://huggingface.co/mcp

Configuration:

Amp can be configured using a JSON settings file located at /root/.config/amp/settings.json. All settings use the "amp." prefix.

Settings reference:

  amp.notifications.enabled
      Enable system sound notifications when agent completes tasks
  amp.notifications.system.enabled
      Enable system notifications when terminal is not focused
  amp.mcpServers
      Model Context Protocol servers to connect to for additional tools
  amp.tools.disable
      Array of tool names to disable. Use 'builtin:toolname' to disable only the builtin tool with that name (allowing an MCP server to provide a tool
      by that name).
  amp.tools.enable
      Array of tool name patterns to enable. Supports glob patterns (e.g., 'mcp__metabase__*'). If not set, all tools are enabled. If set, only
      matching tools are enabled.
  amp.network.timeout
      How many seconds to wait for network requests to the Amp server before timing out
  amp.permissions
      Permission rules for tool calls. See amp permissions --help
  amp.guardedFiles.allowlist
      Array of file glob patterns that are allowed to be accessed without confirmation. Takes precedence over the built-in denylist.
  amp.bitbucketToken
      Personal access token for Bitbucket Enterprise. Used with a workspace-level Bitbucket connection configured by an admin.
  amp.dangerouslyAllowAll
      Disable all command confirmation prompts (agent will execute all commands without asking)
  amp.terminal.animation
      Set to false to disable terminal animations (or use the equivalent NO_ANIMATION=1 env var)
  amp.terminal.theme
      Color theme for the CLI. Built-in: terminal, dark, light, catppuccin-mocha, solarized-dark, solarized-light, gruvbox-dark-hard, nord. Custom
      themes: ~/.config/amp/themes/<name>/colors.toml
  amp.experimental.modes
      Enable experimental agent modes by name. Available modes: deep
  amp.fuzzy.alwaysIncludePaths
      Glob patterns for paths that should always be included in fuzzy file search, even if gitignored
  amp.skills.path
      Path to additional directories containing skills. Supports colon-separated paths (semicolon on Windows). Use ~ for home directory.
  amp.toolbox.path
      Path to the directory containing toolbox scripts. Supports colon-separated paths.
  amp.git.commit.coauthor.enabled
      Enable adding Amp as co-author in git commits
  amp.git.commit.ampThread.enabled
      Enable adding Amp-Thread trailer in git commits
  amp.proxy
      Proxy URL used for both HTTP and HTTPS requests to the Amp server
  amp.updates.mode
      Control update checking behavior: "warn" shows update notifications, "disabled" turns off checking, "auto" automatically runs update.
  amp.showCosts
      Set to false to hide costs while working on a thread

Example configuration:

{
  "amp.notifications.enabled": true,
  "amp.notifications.system.enabled": true,
  "amp.mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-filesystem",
        "/path/to/allowed/dir"
      ]
    }
  },
  "amp.tools.disable": [
    "browser_navigate",
    "builtin:edit_file"
  ],
  "amp.network.timeout": 30,
  "amp.permissions": [
    {
      "tool": "Bash",
      "action": "ask",
      "matches": {
        "cmd": [
          "git push*",
          "git commit*",
          "git branch -D*",
          "git checkout HEAD*"
        ]
      }
    }
  ],
  "amp.guardedFiles.allowlist": [],
  "amp.dangerouslyAllowAll": false,
  "amp.terminal.animation": true,
  "amp.terminal.theme": "terminal",
  "amp.experimental.modes": [],
  "amp.fuzzy.alwaysIncludePaths": [],
  "amp.git.commit.coauthor.enabled": true,
  "amp.git.commit.ampThread.enabled": true,
  "amp.updates.mode": "auto",
  "amp.showCosts": true
}


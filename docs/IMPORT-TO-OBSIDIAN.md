# Importing Documentation to Obsidian

This document explains how to import the FinRobot documentation into your Obsidian vault.

## Documentation Files Created

All documentation files have been created in the `docs/` directory:

1. **README.md** - Main documentation index
2. **00-Project-Overview.md** - Project introduction and overview
3. **01-Getting-Started.md** - Installation and setup guide
4. **02-Architecture.md** - System architecture documentation
5. **03-Agent-Workflows.md** - Agent workflow patterns
6. **04-Development-Guide.md** - Development guide for extending FinRobot
7. **05-Data-Sources.md** - Data source reference guide
8. **06-Functional-Modules.md** - Functional module reference
9. **07-Testing-Guide.md** - Testing strategies and examples
10. **08-Deployment-Guide.md** - Deployment and production guide

## Method 1: Copy Files to Obsidian Vault

### Steps

1. **Locate your Obsidian vault folder**
   - Default location: `~/Documents/Obsidian/` or custom location
   - Or create a new vault: `File > New Vault`

2. **Create a FinRobot folder in your vault**
   ```bash
   mkdir ~/Documents/Obsidian/FinRobot
   ```

3. **Copy all documentation files**
   ```bash
   cp -r /Users/lxupkzwjs/Developer/eval/FinRobot/docs/* ~/Documents/Obsidian/FinRobot/
   ```

4. **Open the vault in Obsidian**
   - The files will appear in the file explorer
   - Internal links using `[[...]]` will work automatically

## Method 2: Use Obsidian MCP (Model Context Protocol)

If you have Obsidian MCP configured:

1. **Check MCP configuration**
   - Ensure Obsidian MCP server is running
   - Verify vault path in MCP settings

2. **Use MCP to import files**
   - The files are ready in `docs/` directory
   - Use MCP commands to copy to your Obsidian vault

## Method 3: Symbolic Link (Advanced)

Create a symbolic link to keep files in sync:

```bash
# Create link in Obsidian vault
ln -s /Users/lxupkzwjs/Developer/eval/FinRobot/docs ~/Documents/Obsidian/FinRobot
```

**Note**: This keeps files synchronized - changes in the repo will reflect in Obsidian.

## Obsidian Features

### Internal Links

The documentation uses Obsidian-style internal links:
- `[[00-Project-Overview]]` - Links to Project Overview
- `[[01-Getting-Started]]` - Links to Getting Started
- All links are relative and will work automatically in Obsidian

### Graph View

Obsidian will automatically create a graph view showing:
- Connections between documents
- Document relationships
- Navigation paths

### Search

Use Obsidian's search (`Cmd/Ctrl + O`) to:
- Find specific topics
- Search across all documentation
- Use tags and filters

### Tags (Optional)

You can add tags to documents for better organization:
```markdown
#tags: #finrobot #documentation #guide
```

## Recommended Obsidian Settings

1. **Enable Wikilinks**: Settings > Files & Links > Use `[[Wikilinks]]`
2. **Auto-update internal links**: Settings > Files & Links > Automatically update internal links
3. **Show frontmatter**: Settings > Editor > Show frontmatter

## Customization

### Add Frontmatter

You can add frontmatter to each document:

```markdown
---
title: Project Overview
tags: [finrobot, overview]
created: 2024-01-01
---
```

### Create MOCs (Maps of Content)

Create an index note that links to all documents:

```markdown
# FinRobot Documentation

## Getting Started
- [[00-Project-Overview]]
- [[01-Getting-Started]]

## Core Documentation
- [[02-Architecture]]
- [[03-Agent-Workflows]]
- [[04-Development-Guide]]

## Reference
- [[05-Data-Sources]]
- [[06-Functional-Modules]]
- [[07-Testing-Guide]]
- [[08-Deployment-Guide]]
```

## Troubleshooting

### Links Not Working

- Ensure files are in the same folder
- Check that Wikilinks are enabled in Obsidian settings
- Verify file names match exactly (case-sensitive)

### Files Not Appearing

- Refresh Obsidian (Cmd/Ctrl + R)
- Check file permissions
- Verify vault is open

### MCP Not Working

- Check MCP server status
- Verify vault path configuration
- Check MCP logs for errors

## Next Steps

1. Import files to your Obsidian vault
2. Open README.md to start exploring
3. Use the graph view to see document relationships
4. Customize with tags and frontmatter as needed

## Support

For issues with:
- **Documentation content**: See README.md
- **Obsidian setup**: Check Obsidian documentation
- **MCP integration**: Check MCP server documentation


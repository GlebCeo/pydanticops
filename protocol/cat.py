def cat_block(filename: str, language: str, content: str) -> str:
    return f"📦 CAT: `{filename}`\n```{language}\n{content}\n```"

def cat_shell(command: str, output: str) -> str:
    return f"💻 CAT: `shell`\n```bash\n$ {command}\n{output}\n```"

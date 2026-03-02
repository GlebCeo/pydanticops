from protocol.cat import cat_block, cat_shell

def test_cat_block_format():
    result = cat_block("test.yml", "yaml", "key: value")
    assert "📦 CAT:" in result
    assert "test.yml" in result
    assert "```yaml" in result
    assert "key: value" in result

def test_cat_shell_format():
    result = cat_shell("docker ps", "CONTAINER ID...")
    assert "💻 CAT:" in result
    assert "docker ps" in result

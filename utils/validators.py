import re

def is_valid_url(url: str) -> bool:
    """
    Valida que la URL comience con protocolo https:// como regla básica.
    """
    pattern = re.compile(r'^https://.*')
    return bool(pattern.match(url))

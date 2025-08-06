def has_any_value(*values) -> bool:
    """Retorna True si al menos uno de los valores no es None, de lo contrario False."""
    return any(value is not None for value in values)

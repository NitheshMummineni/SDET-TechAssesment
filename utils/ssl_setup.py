"""Use the OS certificate store so HTTPS works behind corporate TLS inspection."""


def enable_system_certificate_store() -> None:
    """
    On macOS/Windows, Python does not use the system keychain by default.

    truststore patches ssl to honor enterprise roots installed on the machine
    (the same roots curl and browsers typically trust).
    """
    try:
        import truststore

        truststore.inject_into_ssl()
    except ImportError:
        pass
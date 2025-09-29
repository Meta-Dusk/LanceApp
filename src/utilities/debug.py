import ctypes


def debug_msg(msg: str, handler: str = "DEBUG", debug: bool = False):
    if debug:
        print(f"[{handler}] {msg}")
        
def get_full_username():
    """(Only works in Windows) Returns the user currently logged in the pc."""
    GetUserNameEx = ctypes.windll.secur32.GetUserNameExW
    NameDisplay = 3  # NameDisplay gives full name

    size = ctypes.pointer(ctypes.c_ulong(0))
    GetUserNameEx(NameDisplay, None, size)

    name_buffer = ctypes.create_unicode_buffer(size.contents.value)
    GetUserNameEx(NameDisplay, name_buffer, size)
    return name_buffer.value
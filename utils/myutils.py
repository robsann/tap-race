from pydoc import describe
from typing import Any
from pprint import pprint

# Display private and public functions of any object
def info(var: Any) -> None:
    funcs_priv = [func for func in dir(var) if func[0] == "_"]
    funcs_publ = [func for func in dir(var) if func[0] != "_"]

    print(f'Private Functions\n'
          f'{funcs_priv}\n\n'
          f'Public Functions\n'
          f'{funcs_publ}\n\n'
          f'Type: {type(var)}\n'
          f'Describe: {describe(var)}\n')

'''
Print attributes and methods of a object with their types
Usage:  
    >>> from kivymd.app import MDApp
    >>> obj_prop_type(MDApp())
'''
def ObjInfo(obj: Any) -> None:
    print("\nOBJECT ATTRIBUTES AND METHODS")

    '''ATTRIBUTES'''
    # Filter only attributes (non-callable)
    attributes = [a for a in dir(obj) if not callable(getattr(obj, a)) and not a.startswith("__")]
    attributes_class = [str(type(getattr(obj, a))) for a in dir(obj) \
                        if not callable(getattr(obj, a)) and not a.startswith("__")]

    # Clean data type field
    attributes_class = [a[a.index("'") + 1:-2] for a in attributes_class]

    # Convert zip to list and sort by tuple's second element
    attributes_tuple = list(zip(attributes, attributes_class))
    attributes_tuple = sorted(attributes_tuple, key=lambda x: x[1])

    '''METHODS'''
    # Filter only methods
    methods = [m for m in dir(obj) if callable(getattr(obj, m)) and not m.startswith("__")]
    methods_class = [str(getattr(obj, m)) for m in dir(obj) \
                     if callable(getattr(obj, m)) and not m.startswith("__")]

    # Clean data type field
    methods_class = [m[14:m.index(" of <")] if m[:6] == "<bound" else m for m in methods_class]
    methods_class = [m[10:m.index(" at ")] if m[:6] == "<funct" else m for m in methods_class]
    methods_class = [m[12:m.index(" at ")] if m[:8] == "<cyfunct" else m for m in methods_class]
    methods_class = [m[12:m.index(" at ")] if m[:8] == "<cyfunct" else m for m in methods_class]

    # Convert zip to list and sort by tuple's second element
    methods_tuple = list(zip(methods, methods_class))
    methods_tuple = sorted(methods_tuple, key=lambda x: x[1])

    '''PRINT'''
    obj_class = repr(obj)
    if "'" in obj_class:
        print(f"\nClass: {obj_class[8:-2]}")
    elif " object at" in obj_class:
        print(f"\nClass: {obj_class[1:obj_class.index(" object at")]}")
    else:
        print(f"\nClass: {obj_class}")

    size_a = len(max(attributes, key=len)) + 1
    size_m = len(max(methods, key=len)) + 1

    print(f"\nAttributes{"":<{size_a - 10}}| Class")
    print("=============================================")
    for a, t in attributes_tuple:
    # for a, t in zip(attributes, attributes_class):
        print(f"{a:<{size_a}}| {t}")

    print(f"\nMethods{"":<{size_m - 7}}| Class")
    print("=============================================")
    for m, t in methods_tuple:
    # for m, t in zip(methods, methods_class):
        print(f"{m:<{size_m}}| {t}")




# from kivymd.app import MDApp
# obj_prop_type(MDApp())
# info(MDApp)
# from kivy.lang import Builder
# obj_prop_type(Builder)
# from kivy.uix.widget import Widget
# obj_prop_type(Widget())
# from kivymd.theming import ThemeManager
# obj_prop_type(ThemeManager())
# from kivymd.uix.screen import MDScreen
# obj_prop_type(MDScreen)

# obj_prop_type(int())

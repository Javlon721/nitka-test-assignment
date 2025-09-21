import datetime


def print_shifts(msg: str):
    print(msg)
    print()


def custom_serialization(data: list[any]) -> list[str]:
    '''
        This fn can be definitly modified 
        so for simplicity and time consuption to solve this i make it redundantly
    '''
    result = []
    
    for value in data:
        new_value = None
        match value:
            case str():
                new_value = value
            case int():
                new_value = str(value)
            case list():
                new_value = arr_to_str(value)
            case datetime.datetime():
                new_value = str(value)
            case _:
                raise ValueError(f"Type {type(value)} is not implemented")

        result.append(new_value)

    return result


def arr_to_str(data: list[any], delimiter: str = ', ') -> str:
    return delimiter.join([str(item) for item in data])
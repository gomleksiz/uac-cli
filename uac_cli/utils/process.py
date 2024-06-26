import json
import click
from jsonpath_ng import jsonpath, parse
import re

def snake_to_camel(snake_case_str):
    """Converts a snake_case string to camelCase.

    Args:
        snake_case_str: The string in snake_case format.

    Returns:
        The converted string in camelCase format.
    """
    components = snake_case_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def process_output(output, select, response, text=False, binary=False):
    if output:
        if binary:
            # write response to a binary file
            output.write(response)
        else:
            if text:
                output.write(f"{response.get('response', '')}".replace('\\n', '\n').encode())
            else:
                output.write(json.dumps(response, indent=4))
    
    if select:
        jsonpath_expr = parse(select)
        result = [str(match.value) for match in jsonpath_expr.find(response)]
        click.echo("\n".join(result))
    else:
        if output is None:
            if binary:
                click.echo(response)
            else:
                if text:
                    click.echo(response.get("response", "").replace("\\n", "\n"))
                else:
                    click.echo(json.dumps(response, indent=4))
                

def process_input(args, input=None, ignore_ids=None, binary=False):
    vars_dict = dict(var.split('=', 1) for var in args)
    if ignore_ids is not None:
        vars_dict["retain_sys_ids"] = not ignore_ids
    if input:
        payload = input.read()
        if not binary:    
            if not isinstance(payload, dict):
                payload = json.loads(payload)
            for var in vars_dict:
                _var = snake_to_camel(var)
                value = input_value_parsing(vars_dict[var])
                if var in payload:
                    payload[var] = value
                elif _var in payload:
                    payload[_var] = value
            vars_dict["payload"] = payload
        else:
            vars_dict["data"] = payload
    return vars_dict

def input_value_parsing(value):
    if not isinstance(value, str):
        return value
    
    if value.lower() == ":none:":
        return None
    elif value.lower() == ":false:":
        return False
    elif value.lower() == ":true:":
        return True
    elif value == ":[]:":
        return []
    elif value == ":{}:":
        return {}
    elif re.match(r'^:\d+:$', value):
        return int(value.strip(":"))
    else:
        return value
    

def create_payload(args):
    vars_dict = dict(var.split('=') for var in args)
    payload = {}
    for k, v in vars_dict.items():
        payload[k] = v
    return payload
        
import collections

def hamburger_creator(data):

    valid_burger = True
    keys = ['nombre', 'precio', 'descripcion', 'imagen']
    data_keys = data.keys()

    for key in keys: # First Check if information keys are valid
        if key not in data_keys:
            valid_burger = False
    
    if valid_burger:
        if not (isinstance(data['nombre'], str) and 
            isinstance(data['precio'], int) and isinstance(data['descripcion'], str) and isinstance(data['imagen'], str)):
                valid_burger=False
        else:
            if not (any(c.isalpha() for c in data['nombre']) and any(c.isalpha() for c in data['descripcion']) and any(c.isalpha() for c in data['imagen'])):
            #if not (() or () or ()):  # any(d.isalpha() for d in c)
            #if not (len(data['nombre']) > 0 and len(data['descripcion']) > 0 and len(data['imagen']) > 0):
            # Valid Burger
                valid_burger = False
    
    if valid_burger:
        # Valid
        response = {'status': 'valid input'}
        return response
    else:
        response = {'status': 'invalid input'}
        return response
    
def hamburger_search_by_id(id):
    if not id.isdigit():
        response = {'status': 'invalid id'}
        return response
    response = {'status': 'valid id'}
    return response

def ingredient_creator(data):

    valid_ingredient = True
    keys = ['nombre', 'descripcion']
    data_keys = data.keys()

    if not collections.Counter(keys) == collections.Counter(data_keys):
        valid_ingredient = False
    
    if valid_ingredient:
        for key in data_keys:
            if not isinstance(data[key], str):
                valid_ingredient = False
            else:
                if not any(c.isalpha() for c in data[key]):
                    valid_ingredient = False
    
    if valid_ingredient:
        response = {'status': 'valid input'}
    else:
        response = {'status': 'invalid input'}
    return response

def ingredient_search_by_id(id):
    if not id.isdigit():
        response = {'status': 'invalid id'}
        return response
    response = {'status': 'valid id'}
    return response

def hamburger_update(current_data, new_data):

    valid_update = True
    keys = ['nombre', 'precio', 'descripcion', 'imagen']
    new_data_keys = new_data.keys()

    for key in new_data_keys:
        if key not in keys:
            valid_update = False
    
    #for key in keys:
    #    if key not in new_data_keys:
    #        valid_update = False
    
    if "id" in new_data_keys or "ingredientes" in new_data_keys:
        valid_update = False
    
    if valid_update:
        for key in new_data_keys:
            if key == "precio":
                if not isinstance(new_data[key], int):
                    valid_update = False
            else:
                if not isinstance(new_data[key], str):
                    valid_update = False
                else:
                    if not any(c.isalpha() for c in new_data[key]):
                        valid_update = False
        
        #for key in new_data_keys:
        #    if not isinstance(new_data[key])
        #if not (isinstance(new_data["nombre"], str) and isinstance(new_data["precio"], int) and isinstance(new_data["descripcion"], str) and isinstance(new_data["imagen"], str)):
        #    valid_update = False
    
    if valid_update:
        response = {'status': 'valid update'}
    else:
        response = {'status': 'invalid update'}
    return response

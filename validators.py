def hamburger_creator(data):

    valid_burger = True
    keys = ['nombre', 'precio', 'descripcion', 'imagen']
    data_keys = data.keys()

    for key in keys: # First Check if information keys are valid
        if key not in data_keys:
            valid_burger = False
    
    else:
        if not (isinstance(data['nombre'], str) and 
            isinstance(data['precio'], int) and isinstance(data['descripcion'], str) and isinstance(data['imagen'], str)):
            # Valid Burger
            valid_burger = False
    
    if valid_burger:
        # Valid
        response = {'status': 'valid input'}
        return response
    else:
        response = {'status': 'invalid input'}
        return response
    

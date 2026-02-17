def validate_json_response(response):
    required_fields = {'cliente', 'monto', 'fecha', 'tipo_solicitud'}
    
    if not isinstance(response, dict):
        raise ValueError("Response is not a valid JSON object.")
    
    missing_fields = required_fields - response.keys()
    if missing_fields:
        raise ValueError(f"Missing fields in response: {', '.join(missing_fields)}")
    
    return True

def handle_invalid_json(response):
    try:
        validate_json_response(response)
    except ValueError as e:
        print(f"Validation error: {e}")
        return None
    return response
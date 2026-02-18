def validate_json_response(response):
    """Validate and normalize JSON response from AI"""
    if not isinstance(response, dict):
        raise ValueError("Response is not a valid JSON object.")
    
    # Normalize field names: Accept both 'tipo' and 'tipo_solicitud'
    if 'tipo' in response and 'tipo_solicitud' not in response:
        response['tipo_solicitud'] = response.pop('tipo')
    
    # Convert null values to defaults
    if response.get('cliente') is None or response.get('cliente') == '':
        response['cliente'] = 'No especificado'
    if response.get('monto') is None:
        response['monto'] = 0
    if response.get('fecha') is None or response.get('fecha') == '':
        response['fecha'] = '18/02/2026'
    if response.get('tipo_solicitud') is None or response.get('tipo_solicitud') == '':
        response['tipo_solicitud'] = 'Documento'
    
    # Check required fields after normalization
    required_fields = {'cliente', 'monto', 'fecha', 'tipo_solicitud'}
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
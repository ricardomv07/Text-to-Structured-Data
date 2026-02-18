def validate_single_record(record):
    """Validate and normalize a single JSON record"""
    if not isinstance(record, dict):
        raise ValueError("Record is not a valid JSON object.")
    
    # Normalize field names: Accept both 'tipo' and 'tipo_solicitud'
    if 'tipo' in record and 'tipo_solicitud' not in record:
        record['tipo_solicitud'] = record.pop('tipo')
    
    # Convert null values to defaults
    if record.get('cliente') is None or record.get('cliente') == '':
        record['cliente'] = 'No especificado'
    if record.get('monto') is None:
        record['monto'] = 0
    if record.get('fecha') is None or record.get('fecha') == '':
        record['fecha'] = '18/02/2026'
    if record.get('tipo_solicitud') is None or record.get('tipo_solicitud') == '':
        record['tipo_solicitud'] = 'Documento'
    
    # Check required fields after normalization
    required_fields = {'cliente', 'monto', 'fecha', 'tipo_solicitud'}
    missing_fields = required_fields - record.keys()
    if missing_fields:
        raise ValueError(f"Missing fields in record: {', '.join(missing_fields)}")
    
    return True


def validate_json_response(response):
    """
    Validate and normalize JSON response from AI
    Handles both single objects and arrays of objects
    
    Args:
        response: Either a dict (single record) or list of dicts (multiple records)
    
    Returns:
        list: Always returns a list of validated records (even if input was single object)
    """
    # If it's a single object, convert to array
    if isinstance(response, dict):
        validate_single_record(response)
        return [response]
    
    # If it's an array, validate each record
    elif isinstance(response, list):
        if len(response) == 0:
            raise ValueError("Response is an empty array.")
        
        validated_records = []
        for i, record in enumerate(response):
            try:
                validate_single_record(record)
                validated_records.append(record)
            except ValueError as e:
                raise ValueError(f"Error in record {i+1}: {str(e)}")
        
        return validated_records
    
    else:
        raise ValueError("Response must be a JSON object or array of objects.")
    
    return True

def handle_invalid_json(response):
    try:
        validate_json_response(response)
    except ValueError as e:
        print(f"Validation error: {e}")
        return None
    return response
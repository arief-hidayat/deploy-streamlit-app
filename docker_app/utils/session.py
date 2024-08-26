import uuid


def generate_session_id():
    # Generate a UUID and extract its hex representation
    uuid_hex = uuid.uuid4().hex

    # Extract parts of the UUID to fit the desired pattern
    digits = uuid_hex[:4]  # Use the first 4 characters for digits
    chars = uuid_hex[4:7]  # Use the next 3 characters for letters

    # Construct the pattern (1a23b-4c)
    pattern = f"{digits[0]}{chars[0]}{digits[1:3]}{chars[1]}-{digits[3]}{chars[2]}"
    print("Session ID: " + str(pattern))
    return str(pattern)

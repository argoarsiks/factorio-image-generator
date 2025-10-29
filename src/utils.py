def generate_signal_id(index: int) -> str:
    symbols = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    
    if index < len(symbols):
        return symbols[index]
import enum

class LogEnumItem(enum.Enum):
    EXEC = 'EXEC'  # Execution Free or With tests
    SELF = 'SELF'  # Self evaluation
    MOVE = 'MOVE'  # Interaction with tasks without execution 
    GAME = 'GAME'  # Game changes or setup
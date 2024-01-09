import bcrypt

# Function to hash a password
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

# Function to verify a password
def verify_password(login_attempt, hashed_password):
    return bcrypt.checkpw(login_attempt.encode('utf-8'), hashed_password)
# Password Settings

## FORCE_COMPLEX
**Default**: `True` (Boolean)

Flag that determines whether to force complex passwords, when set to True, Onyx will require all new account passwords to meet the following:

* 8 Characters
* 1 Uppercase Character
* 1 Lowercase Character
* 1 Special Char
* 1 Number

## PASSWORD_SCHEMES
**Default**: `["bcrypt"]` (List(String))

Hash algorithms to support.

## PASSWORD_SCHEMES_DEPRECATED
**Default**: `["auto"] (List(String))

Hash algorithms that should be deprecated.

## SALT_SIZE
**Default**: `32` (Int)

The number of chars to salt passwords with.

### Salt Algorithm
Password salting in Onyx is a bit different than most other systems. We use Python's secrets.choice() method to generate a unique salt for each user and to determine which char position to insert the salt in the password. This makes reversing hashes to find passwords a little bit more difficult than just salting and hashing alone.

## PWD_CONTEXT
The PWD_CONTEXT object is a reference class of CryptContext that provides a number of handy features to validate passwords.